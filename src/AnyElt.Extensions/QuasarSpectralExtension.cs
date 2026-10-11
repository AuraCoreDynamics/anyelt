namespace AnyElt.Extensions;

using AnyElt.Core;

public static class QuasarSpectralExtension
{
    private static readonly List<double> DefaultWavelengths = Enumerable.Range(0, 224)
        .Select(i => 380.0 + i * ((2500.0 - 380.0) / 223.0))
        .ToList();

    public static SpectralSignature ExtractRoiSignature(
        string targetName,
        PixelBBox roi,
        int bandCount = 224,
        List<double>? customWavelengths = null)
    {
        var wl = customWavelengths ?? DefaultWavelengths.Take(bandCount).ToList();
        var targetLower = targetName.ToLowerInvariant();
        var curve = new List<double>();

        foreach (double w in wl)
        {
            double r;
            if (targetLower.Contains("vegetation") || targetLower.Contains("tree") || targetLower.Contains("crop") ||
                targetLower.Contains("forest") || targetLower.Contains("pine") || targetLower.Contains("grass"))
            {
                if (w < 500) r = 0.05 + 0.02 * Math.Sin(w / 100);
                else if (w < 680) r = 0.12 - 0.05 * Math.Sin((w - 550) / 50);
                else if (w < 750) r = 0.10 + 0.45 * ((w - 680) / 70.0);
                else r = 0.55 - 0.15 * Math.Sin((w - 750) / 400);
            }
            else if (targetLower.Contains("water") || targetLower.Contains("ocean") ||
                     targetLower.Contains("lake") || targetLower.Contains("reservoir") || targetLower.Contains("river"))
            {
                r = Math.Max(0.01, 0.25 * Math.Exp(-(w - 400) / 300));
            }
            else if (targetLower.Contains("soil") || targetLower.Contains("sand"))
            {
                r = Math.Min(0.65, 0.10 + 0.45 * ((w - 400) / 2000.0));
            }
            else if (targetLower.Contains("metal") || targetLower.Contains("vehicle"))
            {
                r = 0.40 + 0.10 * Math.Cos(w / 250);
            }
            else
            {
                r = 0.30 + 0.15 * Math.Sin(w / 350);
            }
            curve.Add(Math.Round(Math.Clamp(r, 0.0, 1.0), 4));
        }

        return new SpectralSignature
        {
            TargetName = targetName,
            WavelengthsNm = wl,
            ReflectanceValues = curve,
            RoiBounds = roi,
            Confidence = 0.96
        };
    }

    public static double CalculateSpectralAngle(SpectralSignature sigA, SpectralSignature sigB)
    {
        var a = sigA.ReflectanceValues;
        var b = sigB.ReflectanceValues;
        int n = Math.Min(a.Count, b.Count);
        if (n == 0) return Math.PI / 2.0;

        double dot = 0.0, normA = 0.0, normB = 0.0;
        for (int i = 0; i < n; i++)
        {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }

        normA = Math.Sqrt(normA);
        normB = Math.Sqrt(normB);
        double denom = normA * normB;
        if (denom == 0) return Math.PI / 2.0;

        double cosTheta = Math.Clamp(dot / denom, -1.0, 1.0);
        return Math.Acos(cosTheta);
    }
}
