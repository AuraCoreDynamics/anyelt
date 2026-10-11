namespace AnyElt.Core;

public class EltBridge
{
    public IEltAdapter Source { get; }
    public IEltAdapter Target { get; }

    public EltBridge(IEltAdapter source, IEltAdapter target)
    {
        Source = source;
        Target = target;
    }

    public ViewportState SyncViewport()
    {
        var srcVp = Source.GetViewport();

        if (Target.HasCapability(EltCapability.GroundRoam))
        {
            if (srcVp.CenterGeo != null)
            {
                return Target.RoamToGeo(srcVp.CenterGeo.Lat, srcVp.CenterGeo.Lon, srcVp.ZoomLevel);
            }
            else if (srcVp.CenterPixel != null && Source.CurrentImage != null)
            {
                var geo = Source.ProjectPixelToGround(Source.CurrentImage.Uri, srcVp.CenterPixel);
                return Target.RoamToGeo(geo.Lat, geo.Lon, srcVp.ZoomLevel);
            }
        }

        if (Target.HasCapability(EltCapability.SensorRoam) && srcVp.CenterPixel != null)
        {
            return Target.RoamToPixel(srcVp.CenterPixel.X, srcVp.CenterPixel.Y, srcVp.ZoomLevel);
        }

        throw new BridgingException(Source.Name, Target.Name, "Target ELT does not support a compatible navigation space for viewport sync.");
    }

    public ImageChip TransferChip(ChipRequest request)
    {
        var chip = Source.ExtractChip(request);

        if (Target.HasCapability(EltCapability.DirectLoading))
        {
            try
            {
                Target.LoadImage(chip.SourceUri);
            }
            catch
            {
                // Non-fatal if target just receives the binary chip in-memory
            }
        }

        return chip;
    }

    public CatalogItem SearchAndLoad(CatalogQuery query)
    {
        if (!Source.HasCapability(EltCapability.CatalogSearch))
        {
            throw new BridgingException(Source.Name, Target.Name, "Source ELT does not support Catalog Search.");
        }

        if (!Target.HasCapability(EltCapability.DirectLoading))
        {
            throw new BridgingException(Source.Name, Target.Name, "Target ELT does not support Direct Loading.");
        }

        var items = Source.QueryCatalog(query);
        if (items.Count == 0)
        {
            throw new BridgingException(Source.Name, Target.Name, "No catalog items matched query.");
        }

        var selected = items[0];
        string loadUri = selected.DownloadUri ?? $"catalog://{selected.ItemId}";
        Target.LoadImage(loadUri);
        return selected;
    }
}

public class EltSessionBroker
{
    private readonly Dictionary<string, IEltAdapter> _adapters = new(StringComparer.OrdinalIgnoreCase);

    public void Register(IEltAdapter adapter)
    {
        _adapters[adapter.EltType] = adapter;
    }

    public IEltAdapter? Get(string eltType) => _adapters.GetValueOrDefault(eltType);

    public IReadOnlyCollection<IEltAdapter> RegisteredAdapters => _adapters.Values;

    public Dictionary<string, ViewportState> BroadcastRoamGeo(double lat, double lon, double? zoom = null)
    {
        var results = new Dictionary<string, ViewportState>();
        foreach (var (key, adapter) in _adapters)
        {
            if (adapter.HasCapability(EltCapability.GroundRoam))
            {
                try
                {
                    results[key] = adapter.RoamToGeo(lat, lon, zoom);
                }
                catch
                {
                    // Ignore broadcast failure on individual adapter
                }
            }
        }
        return results;
    }

    public IEltAdapter? FindBestAdapter(EltCapability requiredCapabilities)
    {
        var candidates = _adapters.Values
            .Where(a => (a.Capabilities & requiredCapabilities) == requiredCapabilities)
            .OrderByDescending(a => System.Numerics.BitOperations.PopCount((ulong)a.Capabilities))
            .ToList();

        return candidates.FirstOrDefault();
    }
}
