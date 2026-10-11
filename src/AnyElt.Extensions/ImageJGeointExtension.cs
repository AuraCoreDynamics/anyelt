namespace AnyElt.Extensions;

using AnyElt.Core;

public static class ImageJGeointExtension
{
    public static ImageMetadata SynthesizeGeointMetadata(string uri, int width = 2048, int height = 2048)
    {
        double centerLat = 38.8951;
        double centerLon = -77.0364;
        double dLat = 0.05;
        double dLon = 0.05;

        var bbox = new GeoBBox(
            MinLon: centerLon - dLon / 2.0,
            MinLat: centerLat - dLat / 2.0,
            MaxLon: centerLon + dLon / 2.0,
            MaxLat: centerLat + dLat / 2.0
        );

        var rpc = new RpcCoefficients
        {
            LineOffset = height / 2.0,
            LineScale = height / 2.0,
            SampleOffset = width / 2.0,
            SampleScale = width / 2.0,
            LatOffset = centerLat,
            LatScale = dLat / 2.0,
            LonOffset = centerLon,
            LonScale = dLon / 2.0,
            HeightOffset = 50.0,
            HeightScale = 200.0,
            LineNumCoeff = [0.0, 0.0, 1.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            SampleNumCoeff = [0.0, 1.0, 0.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        };

        var tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["RPC00B"] = "LINE_OFF=1024,SAMP_OFF=1024,LAT_OFF=38.8951,LONG_OFF=-77.0364",
            ["USE00A"] = "SUN_ELEV=46.8,SUN_AZIM=138.2,NIIRS=6.8",
            ["STDIDC"] = "MISSION=IMAGEJ_EXP_2026,PASS=01,OPNUM=1001"
        };

        return new ImageMetadata
        {
            Uri = uri,
            ProductId = "IMAGEJ_NITF_LAYER",
            SensorId = "SCIENTIFIC-PAN/01",
            Format = ImageFormat.Nitf21,
            Width = width,
            Height = height,
            BitDepth = 16,
            BandCount = 1,
            SunElevationDeg = 46.8,
            SunAzimuthDeg = 138.2,
            Niirs = 6.8,
            AcquisitionTimeIso = "2026-10-11T12:00:00Z",
            BBox = bbox,
            Tres = tres,
            Rpc = rpc,
            Extra = new Dictionary<string, object> { ["ImageJ_Extension"] = "Active" }
        };
    }

    public static string GenerateImageJMacro(string scriptName, IEnumerable<string> commands)
    {
        var lines = new List<string>
        {
            $"// AnyElt ImageJ Macro: {scriptName}",
            "setBatchMode(true);"
        };
        lines.AddRange(commands);
        lines.Add("setBatchMode(false);");
        lines.Add("updateDisplay();");
        return string.Join(Environment.NewLine, lines);
    }
}
