namespace AnyElt.Core;

/// <summary>
/// Bitmask flags representing the fine-grained capabilities of an Electronic Light Table (ELT).
/// Adapters self-declare which capabilities they implement.
/// </summary>
[Flags]
public enum EltCapability : long
{
    None = 0,
    DirectLoading = 1L << 0,              // Direct loading of raster files (NITF, GeoTIFF, etc.)
    CatalogSearch = 1L << 1,              // Query internal or remote image catalogs
    RadiometricEnhancement = 1L << 2,     // Brightness, contrast, gamma, sharpen adjustment
    DynamicRangeAdjustment = 1L << 3,     // 1%-99% DRA, Min-Max, Histogram Equalize
    SensorRoam = 1L << 4,                 // Navigation/panning in native sensor pixel coordinates
    GroundRoam = 1L << 5,                 // Navigation/panning in geodetic/ground space
    MensurationShadow = 1L << 6,          // Target height calculation from shadow length and sun elevation
    MensurationDistance = 1L << 7,        // 2D and 3D surface distance and azimuth calculation
    RpcProjection = 1L << 8,              // Forward/inverse RPC00B rational polynomial projection
    ChippingSensor = 1L << 9,             // Extracting chips in native unrectified sensor coordinates
    ChippingGround = 1L << 10,            // Extracting orthorectified geodetic chips
    TreInspection = 1L << 11,             // Parsing MIL-STD-2500 Tagged Record Extensions
    MultiSpectral = 1L << 12,             // Multi-band false color and band combinations
    Hyperspectral = 1L << 13,             // High-dimensional hyperspectral cube slicing
    SpectralSignature = 1L << 14,         // Reflectance wavelength curves from regions of interest
    CrossEltBridge = 1L << 15,            // Cross-ELT data, chip, and command bridging
    ScriptingMacro = 1L << 16,            // Native macro or plugin execution within the ELT engine
    ViewportSync = 1L << 17,              // Real-time synchronization of viewport extents
    Orthorectification = 1L << 18,        // On-the-fly digital elevation model orthorectification

    All = DirectLoading | CatalogSearch | RadiometricEnhancement |
          DynamicRangeAdjustment | SensorRoam | GroundRoam |
          MensurationShadow | MensurationDistance | RpcProjection |
          ChippingSensor | ChippingGround | TreInspection |
          MultiSpectral | Hyperspectral | SpectralSignature |
          CrossEltBridge | ScriptingMacro | ViewportSync |
          Orthorectification
}

public static class CapabilityExtensions
{
    public static IEnumerable<string> ToSlugList(this EltCapability capabilities)
    {
        var list = new List<string>();
        foreach (EltCapability flag in Enum.GetValues<EltCapability>())
        {
            if (flag != EltCapability.None && flag != EltCapability.All && capabilities.HasFlag(flag))
            {
                list.Add(flag.ToString().ToLowerInvariant());
            }
        }
        return list;
    }
}
