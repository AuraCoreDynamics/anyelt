namespace AnyElt.Adapters;

using AnyElt.Core;

public class AuraMistAdapter : BaseEltAdapter
{
    public string? EndpointUrl { get; set; }

    public AuraMistAdapter(string? endpointUrl = null)
        : base("AuraMist Web ELT Adapter", "1.0.0", "auramist")
    {
        EndpointUrl = endpointUrl;
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
        EltCapability.TreInspection |
        EltCapability.ViewportSync |
        EltCapability.Orthorectification;

    public override ImageMetadata GetMetadata(string uri)
    {
        const double centerLat = 38.8951;
        const double centerLon = -77.0364;
        const double d = 0.04;

        var bbox = new GeoBBox(centerLon - d, centerLat - d, centerLon + d, centerLat + d);

        var rpc = new RpcCoefficients
        {
            LineOffset = 1024.0,
            LineScale = 1024.0,
            SampleOffset = 1024.0,
            SampleScale = 1024.0,
            LatOffset = centerLat,
            LatScale = d,
            LonOffset = centerLon,
            LonScale = d,
            LineNumCoeff = [0.0, 0.0, 1.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            SampleNumCoeff = [0.0, 1.0, 0.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        };

        var tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["RPC00B"] = "SUCCESS",
            ["USE00A"] = "SUN_ELEV=46.8,SUN_AZIM=138.2,NIIRS=6.8",
            ["STDIDC"] = "MISSION=AURAMIST_DC_01,PASS=01",
            ["ICHIPB"] = "XFRM_FLAG=00"
        };

        return new ImageMetadata
        {
            Uri = uri,
            ProductId = "AURAMIST_NITF_LAYER",
            SensorId = "WORLDVIEW-03/PAN",
            Format = ImageFormat.Nitf21,
            Width = 2048,
            Height = 2048,
            BitDepth = 16,
            BandCount = 1,
            SunElevationDeg = 46.8,
            SunAzimuthDeg = 138.2,
            Niirs = 6.8,
            AcquisitionTimeIso = "2026-10-11T16:00:00Z",
            BBox = bbox,
            Tres = tres,
            Rpc = rpc,
            Extra = new Dictionary<string, object>
            {
                ["AuraTiles_Backend"] = "Active",
                ["DualSpace"] = "Enabled"
            }
        };
    }
}
