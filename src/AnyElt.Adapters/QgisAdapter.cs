namespace AnyElt.Adapters;

using System.Diagnostics;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using AnyElt.Core;
using AnyElt.Core.IO;

/// <summary>
/// Real QGIS Desktop & PyQGIS Bridge Adapter.
/// Interfaces with QGIS 3.40+ on Windows via:
/// 1. Headless PyQGIS runtime (python-qgis-ltr.bat) for native QgsRasterLayer inspection and analysis.
/// 2. Local JSON-RPC TCP socket bridge (port 9180) to command live QGIS GUI canvas extents and layers.
/// 3. Native binary RasterReader for direct byte-level NITF and GeoTIFF decoding.
/// </summary>
public class QgisAdapter : BaseEltAdapter
{
    private static readonly string[] PossibleQgisBatPaths =
    [
        @"C:\Program Files\QGIS 3.40.8\bin\python-qgis-ltr.bat",
        @"C:\Program Files\QGIS 3.34\bin\python-qgis-ltr.bat",
        @"C:\Program Files\QGIS\bin\python-qgis.bat"
    ];

    public string? QgisPythonBatchPath { get; set; }
    public int RpcPort { get; set; }
    private TcpClient? _rpcClient;

    public QgisAdapter(int rpcPort = 9180, string? qgisPythonBatchPath = null)
        : base("QGIS PyQGIS Bridge Adapter", "1.0.0", "qgis")
    {
        RpcPort = rpcPort;
        QgisPythonBatchPath = qgisPythonBatchPath ?? FindQgisBatchPath();
    }

    private static string? FindQgisBatchPath()
    {
        foreach (var path in PossibleQgisBatPaths)
        {
            if (File.Exists(path)) return path;
        }
        return null;
    }

    public override EltCapability Capabilities =>
        EltCapability.DirectLoading |
        EltCapability.RadiometricEnhancement |
        EltCapability.GroundRoam |
        EltCapability.MensurationDistance |
        EltCapability.ChippingGround |
        EltCapability.TreInspection |
        EltCapability.MultiSpectral |
        EltCapability.ViewportSync;

    public override bool Connect(string? connectionString = null)
    {
        base.Connect(connectionString);

        // Attempt connecting to live QGIS GUI TCP socket bridge
        try
        {
            _rpcClient = new TcpClient();
            var connectTask = _rpcClient.ConnectAsync("sm", RpcPort);
            if (connectTask.Wait(TimeSpan.FromMilliseconds(500)))
            {
                return true;
            }
        }
        catch
        {
            _rpcClient?.Dispose();
            _rpcClient = null;
        }

        // Operational in headless PyQGIS mode if batch exists
        return true;
    }

    public override void Disconnect()
    {
        base.Disconnect();
        try
        {
            _rpcClient?.Close();
            _rpcClient?.Dispose();
        }
        catch { }
        _rpcClient = null;
    }

    public override ImageMetadata GetMetadata(string uri)
    {
        string cleanPath = uri.StartsWith("file://", StringComparison.OrdinalIgnoreCase)
            ? uri.Substring(7)
            : uri;

        // 1. If file exists on disk and PyQGIS is available, query real QgsRasterLayer
        if (File.Exists(cleanPath) && !string.IsNullOrEmpty(QgisPythonBatchPath) && File.Exists(QgisPythonBatchPath))
        {
            var pyMeta = QueryViaPyQgis(cleanPath);
            if (pyMeta != null) return pyMeta;
        }

        // 2. Direct binary inspection via RasterReader
        if (File.Exists(cleanPath))
        {
            var meta = RasterReader.ReadMetadata(cleanPath);
            meta.Extra["QgisEngine"] = "RasterReader_Standalone";
            return meta;
        }

        throw new ImageNotFoundException($"Raster file '{uri}' not found on disk.");
    }

    public override ViewportState RoamToGeo(double lat, double lon, double? zoom = null)
    {
        var vp = base.RoamToGeo(lat, lon, zoom);

        // If connected to live QGIS GUI socket bridge, send canvas extent update
        if (_rpcClient != null && _rpcClient.Connected)
        {
            try
            {
                double span = 0.05 / (zoom ?? 1.0);
                string rpcJson = JsonSerializer.Serialize(new
                {
                    cmd = "set_extent",
                    min_x = lon - span,
                    min_y = lat - span,
                    max_x = lon + span,
                    max_y = lat + span
                }) + "\n";

                byte[] data = Encoding.UTF8.GetBytes(rpcJson);
                _rpcClient.GetStream().Write(data, 0, data.Length);
            }
            catch
            {
                // Non-fatal if socket communication drops
            }
        }

        return vp;
    }

    private ImageMetadata? QueryViaPyQgis(string filePath)
    {
        try
        {
            string escapedPath = filePath.Replace("\\", "/");
            string script = $@"
import sys, json
from qgis.core import QgsApplication, QgsRasterLayer
QgsApplication.setPrefixPath(r'{Path.GetDirectoryName(Path.GetDirectoryName(QgisPythonBatchPath))}\apps\qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()
layer = QgsRasterLayer('{escapedPath}', 'Layer')
if layer.isValid():
    ext = layer.extent()
    res = {{
        'valid': True,
        'width': layer.width(),
        'height': layer.height(),
        'bands': layer.bandCount(),
        'crs': layer.crs().authid(),
        'bbox': [ext.xMinimum(), ext.yMinimum(), ext.xMaximum(), ext.yMaximum()]
    }}
else:
    res = {{'valid': False}}
print('__QGIS_OUT__' + json.dumps(res))
qgs.exitQgis()
";
            var psi = new ProcessStartInfo
            {
                FileName = QgisPythonBatchPath,
                Arguments = $"-c \"{script.Replace("\"", "\\\"").Replace("\r\n", " ").Replace("\n", " ")}\"",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using var proc = Process.Start(psi);
            if (proc == null) return null;

            string output = proc.StandardOutput.ReadToEnd();
            proc.WaitForExit(8000);

            int marker = output.IndexOf("__QGIS_OUT__", StringComparison.Ordinal);
            if (marker >= 0)
            {
                string jsonStr = output.Substring(marker + "__QGIS_OUT__".Length).Trim();
                using var doc = JsonDocument.Parse(jsonStr);
                var root = doc.RootElement;
                if (root.GetProperty("valid").GetBoolean())
                {
                    int w = root.GetProperty("width").GetInt32();
                    int h = root.GetProperty("height").GetInt32();
                    int bands = root.GetProperty("bands").GetInt32();
                    string crs = root.GetProperty("crs").GetString() ?? "EPSG:4326";
                    var bboxArr = root.GetProperty("bbox");
                    double minX = bboxArr[0].GetDouble();
                    double minY = bboxArr[1].GetDouble();
                    double maxX = bboxArr[2].GetDouble();
                    double maxY = bboxArr[3].GetDouble();

                    return new ImageMetadata
                    {
                        Uri = filePath,
                        ProductId = Path.GetFileNameWithoutExtension(filePath),
                        SensorId = "QGIS-PYQGIS-RASTER",
                        Format = filePath.EndsWith(".ntf", StringComparison.OrdinalIgnoreCase) ? ImageFormat.Nitf21 : ImageFormat.GeoTiff,
                        Width = w,
                        Height = h,
                        BitDepth = 16,
                        BandCount = bands,
                        SunElevationDeg = 45.0,
                        BBox = new GeoBBox(minX, minY, maxX, maxY),
                        Tres = new Dictionary<string, string> { ["QGIS_CRS"] = crs },
                        Extra = new Dictionary<string, object>
                        {
                            ["PyQgisExecuted"] = true,
                            ["QgisCrs"] = crs
                        }
                    };
                }
            }
        }
        catch
        {
            // Fallback to RasterReader
        }

        return null;
    }
}
