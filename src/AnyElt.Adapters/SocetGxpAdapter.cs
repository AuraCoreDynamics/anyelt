namespace AnyElt.Adapters;

using AnyElt.Core;

public class SocetGxpAdapter : BaseEltAdapter
{
    public string? WorkspacePath { get; set; }

    public SocetGxpAdapter(string? workspacePath = null)
        : base("BAE Systems SOCET GXP Adapter", "1.0.0", "socet_gxp")
    {
        WorkspacePath = workspacePath;
    }

    public override EltCapability Capabilities =>
        EltCapability.DirectLoading |
        EltCapability.CatalogSearch |
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
        EltCapability.MultiSpectral |
        EltCapability.ViewportSync;

    public override ImageMetadata GetMetadata(string uri)
    {
        const double centerLat = 32.7157;
        const double centerLon = -117.1611;
        const double d = 0.06;

        var bbox = new GeoBBox(centerLon - d, centerLat - d, centerLon + d, centerLat + d);

        var rpc = new RpcCoefficients
        {
            LineOffset = 2048.0,
            LineScale = 2048.0,
            SampleOffset = 2048.0,
            SampleScale = 2048.0,
            LatOffset = centerLat,
            LatScale = d,
            LonOffset = centerLon,
            LonScale = d,
            LineNumCoeff = [0.0, 0.0, 1.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            SampleNumCoeff = [0.0, 1.0, 0.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        };

        var tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["RPC00B"] = "ACTIVE_RIGOROUS",
            ["USE00A"] = "SUN_ELEV=52.4,SUN_AZIM=145.0,NIIRS=7.1",
            ["STDIDC"] = "MISSION=GXP_EXPLOIT_SD,PASS=02",
            ["PIAIMC"] = "CLOUDCVR=00"
        };

        return new ImageMetadata
        {
            Uri = uri,
            ProductId = "SOCET_GXP_PROJECT_PRODUCT",
            SensorId = "GEOEYE-01/MS",
            Format = ImageFormat.Nitf21,
            Width = 4096,
            Height = 4096,
            BitDepth = 16,
            BandCount = 4,
            SunElevationDeg = 52.4,
            SunAzimuthDeg = 145.0,
            Niirs = 7.1,
            AcquisitionTimeIso = "2026-10-10T14:30:00Z",
            BBox = bbox,
            Tres = tres,
            Rpc = rpc,
            Extra = new Dictionary<string, object>
            {
                ["GxpWorkspace"] = WorkspacePath ?? "Default"
            }
        };
    }

    public override IReadOnlyList<CatalogItem> QueryCatalog(CatalogQuery query)
    {
        RequireCapability(EltCapability.CatalogSearch);

        var bbox = query.BBox ?? new GeoBBox(-117.2, 32.6, -117.1, 32.8);
        var items = new List<CatalogItem>
        {
            new CatalogItem
            {
                ItemId = "GXP_XPLORER_ITEM_1001",
                Title = "San Diego Naval Base EO/IR Pass",
                SensorId = query.SensorId ?? "GEOEYE-01",
                AcquisitionTimeIso = "2026-10-10T14:30:00Z",
                BBox = bbox,
                Niirs = 7.1,
                CloudCoverPercent = 0.0,
                DownloadUri = "gxp://catalog/items/1001.ntf",
                Tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
                {
                    ["RPC00B"] = "PRESENT",
                    ["USE00A"] = "SUN_ELEV=52.4"
                }
            },
            new CatalogItem
            {
                ItemId = "GXP_XPLORER_ITEM_1002",
                Title = "Coronado Amphibious Base Multispectral",
                SensorId = "WORLDVIEW-02",
                AcquisitionTimeIso = "2026-10-09T18:15:00Z",
                BBox = bbox,
                Niirs = 6.5,
                CloudCoverPercent = 5.0,
                DownloadUri = "gxp://catalog/items/1002.ntf",
                Tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
                {
                    ["RPC00B"] = "PRESENT",
                    ["USE00A"] = "SUN_ELEV=49.1"
                }
            }
        };

        return items.Take(query.Limit).ToList();
    }
}
