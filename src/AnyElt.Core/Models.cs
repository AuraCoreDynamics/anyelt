namespace AnyElt.Core;

public enum ImageFormat
{
    Nitf21,
    Nitf20,
    GeoTiff,
    CibCadrg,
    Hdf5,
    Envi,
    Mrf,
    Jpeg2000,
    Png,
    Unknown
}

public enum DraMode
{
    None,
    AutoPercentile,
    MinMax,
    HistogramEqualization,
    Linear
}

public record GeoPoint(double Lat, double Lon, double AltM = 0.0);

public record PixelPoint(double X, double Y);

public record GeoBBox(double MinLon, double MinLat, double MaxLon, double MaxLat)
{
    public double CenterLon => (MinLon + MaxLon) / 2.0;
    public double CenterLat => (MinLat + MaxLat) / 2.0;
}

public record PixelBBox(int MinX, int MinY, int MaxX, int MaxY)
{
    public int Width => Math.Max(0, MaxX - MinX);
    public int Height => Math.Max(0, MaxY - MinY);
}

public class RpcCoefficients
{
    public double LineOffset { get; set; } = 0.0;
    public double LineScale { get; set; } = 1.0;
    public double SampleOffset { get; set; } = 0.0;
    public double SampleScale { get; set; } = 1.0;
    public double LatOffset { get; set; } = 0.0;
    public double LatScale { get; set; } = 1.0;
    public double LonOffset { get; set; } = 0.0;
    public double LonScale { get; set; } = 1.0;
    public double HeightOffset { get; set; } = 0.0;
    public double HeightScale { get; set; } = 1.0;

    public double[] LineNumCoeff { get; set; } = new double[20];
    public double[] LineDenCoeff { get; set; } = new double[20] { 1.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 };
    public double[] SampleNumCoeff { get; set; } = new double[20];
    public double[] SampleDenCoeff { get; set; } = new double[20] { 1.0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 };

    public PixelPoint EvaluateForward(double lat, double lon, double height = 0.0)
    {
        double nLat = LatScale != 0 ? (lat - LatOffset) / LatScale : 0.0;
        double nLon = LonScale != 0 ? (lon - LonOffset) / LonScale : 0.0;
        double nHgt = HeightScale != 0 ? (height - HeightOffset) / HeightScale : 0.0;

        double[] u =
        [
            1.0, nLon, nLat, nHgt, nLon * nLat, nLon * nHgt, nLat * nHgt,
            Math.Pow(nLon, 2), Math.Pow(nLat, 2), Math.Pow(nHgt, 2), nLon * nLat * nHgt,
            Math.Pow(nLon, 3), nLon * Math.Pow(nLat, 2), nLon * Math.Pow(nHgt, 2),
            Math.Pow(nLon, 2) * nLat, Math.Pow(nLat, 3), nLat * Math.Pow(nHgt, 2),
            Math.Pow(nLon, 2) * nHgt, Math.Pow(nLat, 2) * nHgt, Math.Pow(nHgt, 3)
        ];

        double lineNum = 0.0, lineDen = 0.0, sampleNum = 0.0, sampleDen = 0.0;
        for (int i = 0; i < 20; i++)
        {
            lineNum += LineNumCoeff[i] * u[i];
            lineDen += LineDenCoeff[i] * u[i];
            sampleNum += SampleNumCoeff[i] * u[i];
            sampleDen += SampleDenCoeff[i] * u[i];
        }

        double nLine = lineDen != 0 ? lineNum / lineDen : 0.0;
        double nSample = sampleDen != 0 ? sampleNum / sampleDen : 0.0;

        double line = nLine * LineScale + LineOffset;
        double sample = nSample * SampleScale + SampleOffset;

        return new PixelPoint(sample, line);
    }
}

public class ImageMetadata
{
    public required string Uri { get; set; }
    public required string ProductId { get; set; }
    public required string SensorId { get; set; }
    public ImageFormat Format { get; set; } = ImageFormat.Nitf21;
    public int Width { get; set; }
    public int Height { get; set; }
    public int BitDepth { get; set; } = 8;
    public int BandCount { get; set; } = 1;
    public double? SunElevationDeg { get; set; }
    public double? SunAzimuthDeg { get; set; }
    public double? Niirs { get; set; }
    public string? AcquisitionTimeIso { get; set; }
    public GeoBBox? BBox { get; set; }
    public Dictionary<string, string> Tres { get; set; } = new(StringComparer.OrdinalIgnoreCase);
    public RpcCoefficients? Rpc { get; set; }
    public Dictionary<string, object> Extra { get; set; } = new();
}

public class RadiometricParameters
{
    public double Brightness { get; set; } = 0.0;
    public double Contrast { get; set; } = 1.0;
    public double Gamma { get; set; } = 1.0;
    public double Sharpen { get; set; } = 0.0;
    public bool Invert { get; set; } = false;
    public DraMode DraMode { get; set; } = DraMode.AutoPercentile;
}

public class ViewportState
{
    public GeoPoint? CenterGeo { get; set; }
    public PixelPoint? CenterPixel { get; set; }
    public double ZoomLevel { get; set; } = 1.0;
    public double RotationDeg { get; set; } = 0.0;
    public RadiometricParameters Radiometrics { get; set; } = new();
    public string? LayerUri { get; set; }
}

public class ChipRequest
{
    public required string ImageUri { get; set; }
    public PixelBBox? SensorBounds { get; set; }
    public GeoBBox? GroundBounds { get; set; }
    public string OutputFormat { get; set; } = "PNG";
    public List<int>? Bands { get; set; }
    public RadiometricParameters? Radiometrics { get; set; }
}

public class ImageChip
{
    public required string ChipId { get; set; }
    public required string SourceUri { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
    public required string Format { get; set; }
    public required byte[] Data { get; set; }
    public PixelBBox? SensorBounds { get; set; }
    public GeoBBox? GroundBounds { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public class MensurationRequest
{
    public required string ImageUri { get; set; }
    public required string CalculationType { get; set; } // SHADOW_HEIGHT, DISTANCE_2D, DISTANCE_3D, AZIMUTH
    public PixelPoint? PointAPixel { get; set; }
    public PixelPoint? PointBPixel { get; set; }
    public GeoPoint? PointAGeo { get; set; }
    public GeoPoint? PointBGeo { get; set; }
    public double? ShadowLengthM { get; set; }
    public double? SunElevationDeg { get; set; }
}

public class MensurationResult
{
    public double CalculatedValue { get; set; }
    public required string Unit { get; set; }
    public required string FormulaApplied { get; set; }
    public double ConfidenceScore { get; set; } = 1.0;
    public Dictionary<string, object> Details { get; set; } = new();
}

public class CatalogQuery
{
    public GeoBBox? BBox { get; set; }
    public string? SensorId { get; set; }
    public string? StartTimeIso { get; set; }
    public string? EndTimeIso { get; set; }
    public double? MinNiirs { get; set; }
    public double? MaxCloudCoverPercent { get; set; }
    public int Limit { get; set; } = 50;
}

public class CatalogItem
{
    public required string ItemId { get; set; }
    public required string Title { get; set; }
    public required string SensorId { get; set; }
    public required string AcquisitionTimeIso { get; set; }
    public required GeoBBox BBox { get; set; }
    public double? Niirs { get; set; }
    public double? CloudCoverPercent { get; set; }
    public string? DownloadUri { get; set; }
    public string? ThumbnailUri { get; set; }
    public Dictionary<string, string> Tres { get; set; } = new(StringComparer.OrdinalIgnoreCase);
}

public class SpectralSignature
{
    public required string TargetName { get; set; }
    public required List<double> WavelengthsNm { get; set; }
    public required List<double> ReflectanceValues { get; set; }
    public PixelBBox? RoiBounds { get; set; }
    public double Confidence { get; set; } = 1.0;
}
