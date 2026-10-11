namespace AnyElt.Core;

/// <summary>
/// Universal interface for Electronic Light Table (ELT) adapters.
/// Exposes exploitation, navigation, mensuration, chipping, and catalog verbs.
/// </summary>
public interface IEltAdapter
{
    string Name { get; }
    string Version { get; }
    string EltType { get; }
    EltCapability Capabilities { get; }

    bool HasCapability(EltCapability capability);
    bool Connect(string? connectionString = null);
    void Disconnect();
    bool IsConnected { get; }

    ImageMetadata LoadImage(string uri);
    ImageMetadata GetMetadata(string uri);
    ImageMetadata? CurrentImage { get; }

    ViewportState GetViewport();
    ViewportState SetViewport(ViewportState viewport);
    ViewportState RoamToGeo(double lat, double lon, double? zoom = null);
    ViewportState RoamToPixel(double x, double y, double? zoom = null);

    RadiometricParameters ApplyRadiometrics(RadiometricParameters parameters);
    ImageChip ExtractChip(ChipRequest request);
    MensurationResult Mensurate(MensurationRequest request);
    IReadOnlyList<CatalogItem> QueryCatalog(CatalogQuery query);

    GeoPoint ProjectPixelToGround(string uri, PixelPoint pixel);
    PixelPoint ProjectGroundToPixel(string uri, GeoPoint geo);
}
