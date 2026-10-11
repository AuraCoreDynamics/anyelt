namespace AnyElt.Adapters;

using AnyElt.Core;

public class RemoteViewAdapter : BaseEltAdapter
{
    public string? ExecutablePath { get; set; }

    public RemoteViewAdapter(string? executablePath = null)
        : base("Textron Systems RemoteView Adapter", "1.0.0", "remoteview")
    {
        ExecutablePath = executablePath;
    }

    public override EltCapability Capabilities =>
        EltCapability.DirectLoading |
        EltCapability.RadiometricEnhancement |
        EltCapability.DynamicRangeAdjustment |
        EltCapability.SensorRoam |
        EltCapability.GroundRoam |
        EltCapability.MensurationShadow |
        EltCapability.MensurationDistance |
        EltCapability.RpcProjection |
        EltCapability.ChippingSensor |
        EltCapability.ChippingGround |
        EltCapability.TreInspection;

    public override ImageMetadata GetMetadata(string uri)
    {
        const double centerLat = 36.8508;
        const double centerLon = -75.9779;
        const double d = 0.05;

        var bbox = new GeoBBox(centerLon - d, centerLat - d, centerLon + d, centerLat + d);

        var rpc = new RpcCoefficients
        {
            LineOffset = 1500.0,
            LineScale = 1500.0,
            SampleOffset = 1500.0,
            SampleScale = 1500.0,
            LatOffset = centerLat,
            LatScale = d,
            LonOffset = centerLon,
            LonScale = d,
            LineNumCoeff = [0.0, 0.0, 1.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            SampleNumCoeff = [0.0, 1.0, 0.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        };

        var tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["RPC00B"] = "PRESENT",
            ["USE00A"] = "SUN_ELEV=38.2,SUN_AZIM=162.4,NIIRS=6.4",
            ["STDIDC"] = "MISSION=RV_VIRGINIA_BEACH,PASS=04"
        };

        return new ImageMetadata
        {
            Uri = uri,
            ProductId = "REMOTEVIEW_IMAGE_LAYER",
            SensorId = "WORLDVIEW-01/PAN",
            Format = ImageFormat.Nitf21,
            Width = 3000,
            Height = 3000,
            BitDepth = 11,
            BandCount = 1,
            SunElevationDeg = 38.2,
            SunAzimuthDeg = 162.4,
            Niirs = 6.4,
            AcquisitionTimeIso = "2026-10-11T09:45:00Z",
            BBox = bbox,
            Tres = tres,
            Rpc = rpc,
            Extra = new Dictionary<string, object>
            {
                ["RemoteViewBinary"] = ExecutablePath ?? "Detected"
            }
        };
    }
}
