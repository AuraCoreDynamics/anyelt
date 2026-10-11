namespace AnyElt.Adapters;

using AnyElt.Core;

public class QgisAdapter : BaseEltAdapter
{
    public int RpcPort { get; set; }

    public QgisAdapter(int rpcPort = 9180)
        : base("QGIS PyQGIS Bridge Adapter", "1.0.0", "qgis")
    {
        RpcPort = rpcPort;
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

    public override ImageMetadata GetMetadata(string uri)
    {
        const double centerLat = 45.4215;
        const double centerLon = -75.6972;
        const double d = 0.08;

        var bbox = new GeoBBox(centerLon - d, centerLat - d, centerLon + d, centerLat + d);

        var tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["GDAL_METADATA"] = "DRIVER=NITF",
            ["STDIDC"] = "MISSION=QGIS_SAMPLE,PASS=01"
        };

        return new ImageMetadata
        {
            Uri = uri,
            ProductId = "QGIS_RASTER_LAYER",
            SensorId = "SENTINEL-2/MSI",
            Format = ImageFormat.GeoTiff,
            Width = 3600,
            Height = 3600,
            BitDepth = 16,
            BandCount = 12,
            SunElevationDeg = 48.0,
            SunAzimuthDeg = 150.0,
            Niirs = 4.5,
            AcquisitionTimeIso = "2026-10-08T15:20:00Z",
            BBox = bbox,
            Tres = tres,
            Rpc = null,
            Extra = new Dictionary<string, object>
            {
                ["QgisRpcPort"] = RpcPort
            }
        };
    }
}
