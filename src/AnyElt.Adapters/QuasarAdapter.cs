namespace AnyElt.Adapters;

using AnyElt.Core;
using AnyElt.Extensions;

public class QuasarAdapter : BaseEltAdapter
{
    public string? WorkspacePath { get; set; }

    public QuasarAdapter(string? workspacePath = null)
        : base("Quasar / Orange Hyperspectral Adapter", "1.0.0", "quasar")
    {
        WorkspacePath = workspacePath;
    }

    public override EltCapability Capabilities =>
        EltCapability.DirectLoading |
        EltCapability.ChippingSensor |
        EltCapability.MultiSpectral |
        EltCapability.Hyperspectral |
        EltCapability.SpectralSignature;

    public override ImageMetadata GetMetadata(string uri)
    {
        const double centerLat = 37.7749;
        const double centerLon = -122.4194;
        const double d = 0.05;

        var bbox = new GeoBBox(centerLon - d, centerLat - d, centerLon + d, centerLat + d);

        var tres = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["QUASAR_HYPERCUBE"] = "BANDS=224,SPECTRAL_RANGE=380-2500nm",
            ["SENSOR"] = "AVIRIS-CLASS-HYPERSPECTRAL"
        };

        return new ImageMetadata
        {
            Uri = uri,
            ProductId = "QUASAR_HYPERCUBE_DATASET",
            SensorId = "AVIRIS-NG/HYPER",
            Format = ImageFormat.Hdf5,
            Width = 1024,
            Height = 1024,
            BitDepth = 16,
            BandCount = 224,
            SunElevationDeg = 55.0,
            SunAzimuthDeg = 160.0,
            Niirs = null,
            AcquisitionTimeIso = "2026-09-15T18:00:00Z",
            BBox = bbox,
            Tres = tres,
            Rpc = null,
            Extra = new Dictionary<string, object>
            {
                ["QuasarSpectroscopy"] = "Enabled",
                ["WavelengthUnit"] = "nm"
            }
        };
    }

    public SpectralSignature ExtractSpectralSignature(string targetName, PixelBBox roi)
    {
        RequireCapability(EltCapability.SpectralSignature);
        return QuasarSpectralExtension.ExtractRoiSignature(targetName, roi);
    }

    public double CompareSpectralSignatures(SpectralSignature sigA, SpectralSignature sigB)
    {
        return QuasarSpectralExtension.CalculateSpectralAngle(sigA, sigB);
    }
}
