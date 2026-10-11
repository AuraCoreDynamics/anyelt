namespace AnyElt.Adapters;

using AnyElt.Core;

public class ISpyAdapter : BaseEltAdapter
{
    public string? ServiceUrl { get; set; }
    public string? ApiKey { get; set; }

    public ISpyAdapter(string? serviceUrl = null, string? apiKey = null)
        : base("NGA iSPY Catalog Adapter", "1.0.0", "ispy")
    {
        ServiceUrl = serviceUrl;
        ApiKey = apiKey;
    }

    public override EltCapability Capabilities =>
        EltCapability.CatalogSearch |
        EltCapability.ChippingGround |
        EltCapability.TreInspection;

    public override ImageMetadata GetMetadata(string uri)
    {
        const double centerLat = 34.0522;
        const double centerLon = -118.2437;
        const double d = 0.05;

        var bbox = new GeoBBox(centerLon - d, centerLat - d, centerLon + d, centerLat + d);

        var tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["USE00A"] = "SUN_ELEV=41.5,SUN_AZIM=155.0,NIIRS=6.2",
            ["STDIDC"] = "MISSION=ISPY_HARVEST,PASS=12",
            ["PIAIMC"] = "CLOUDCVR=02,GENINT=01"
        };

        return new ImageMetadata
        {
            Uri = uri,
            ProductId = "ISPY_CATALOG_RECORD",
            SensorId = "WORLDVIEW-02/PAN",
            Format = ImageFormat.Nitf21,
            Width = 2048,
            Height = 2048,
            BitDepth = 11,
            BandCount = 1,
            SunElevationDeg = 41.5,
            SunAzimuthDeg = 155.0,
            Niirs = 6.2,
            AcquisitionTimeIso = "2026-10-07T19:00:00Z",
            BBox = bbox,
            Tres = tres,
            Rpc = null,
            Extra = new Dictionary<string, object>
            {
                ["iSPY_Service"] = ServiceUrl ?? "ActiveCatalog"
            }
        };
    }

    public override IReadOnlyList<CatalogItem> QueryCatalog(CatalogQuery query)
    {
        RequireCapability(EltCapability.CatalogSearch);

        var bbox = query.BBox ?? new GeoBBox(-118.3, 34.0, -118.2, 34.1);
        var items = new List<CatalogItem>
        {
            new CatalogItem
            {
                ItemId = "ISPY_RECORD_2026_0901",
                Title = "Los Angeles Port Logistics Recon",
                SensorId = query.SensorId ?? "WORLDVIEW-02",
                AcquisitionTimeIso = "2026-10-07T19:00:00Z",
                BBox = bbox,
                Niirs = 6.2,
                CloudCoverPercent = 2.0,
                DownloadUri = "ispy://catalog/nitf/2026_0901.ntf",
                Tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
                {
                    ["USE00A"] = "SUN_ELEV=41.5",
                    ["STDIDC"] = "MISSION=ISPY_01"
                }
            },
            new CatalogItem
            {
                ItemId = "ISPY_RECORD_2026_0902",
                Title = "Long Beach Terminal Overview",
                SensorId = "GEOEYE-01",
                AcquisitionTimeIso = "2026-10-06T20:15:00Z",
                BBox = bbox,
                Niirs = 6.7,
                CloudCoverPercent = 0.0,
                DownloadUri = "ispy://catalog/nitf/2026_0902.ntf",
                Tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
                {
                    ["USE00A"] = "SUN_ELEV=43.0",
                    ["STDIDC"] = "MISSION=ISPY_02"
                }
            }
        };

        return items.Take(query.Limit).ToList();
    }
}
