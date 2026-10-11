namespace AnyElt.Adapters;

using System.Text;
using System.Text.Json;
using AnyElt.Core;

public static class EltRegistry
{
    private static readonly Dictionary<string, Func<IEltAdapter>> _factories =
        new(StringComparer.OrdinalIgnoreCase)
        {
            ["auramist"] = () => new AuraMistAdapter(),
            ["socet_gxp"] = () => new SocetGxpAdapter(),
            ["remoteview"] = () => new RemoteViewAdapter(),
            ["qgis"] = () => new QgisAdapter(),
            ["ispy"] = () => new ISpyAdapter(),
            ["imagej"] = () => new ImageJAdapter(),
            ["quasar"] = () => new QuasarAdapter()
        };

    public static IEltAdapter Create(string eltType)
    {
        if (!_factories.TryGetValue(eltType, out var factory))
        {
            throw new ArgumentException($"Unknown ELT adapter type: '{eltType}'. Available: {string.Join(", ", _factories.Keys)}");
        }
        return factory();
    }

    public static IReadOnlyList<IEltAdapter> GetAllAdapters() =>
        _factories.Values.Select(f => f()).ToList();

    public static IEltAdapter? FindBestAdapter(EltCapability requiredCapabilities)
    {
        var broker = new EltSessionBroker();
        foreach (var adapter in GetAllAdapters())
        {
            broker.Register(adapter);
        }
        return broker.FindBestAdapter(requiredCapabilities);
    }

    public static string GenerateCapabilityMatrixMarkdown()
    {
        var adapters = GetAllAdapters();
        var capabilities = new[]
        {
            EltCapability.DirectLoading,
            EltCapability.CatalogSearch,
            EltCapability.RadiometricEnhancement,
            EltCapability.DynamicRangeAdjustment,
            EltCapability.SensorRoam,
            EltCapability.GroundRoam,
            EltCapability.MensurationShadow,
            EltCapability.MensurationDistance,
            EltCapability.RpcProjection,
            EltCapability.ChippingSensor,
            EltCapability.ChippingGround,
            EltCapability.TreInspection,
            EltCapability.MultiSpectral,
            EltCapability.Hyperspectral,
            EltCapability.SpectralSignature,
            EltCapability.ScriptingMacro,
            EltCapability.ViewportSync,
            EltCapability.Orthorectification
        };

        var sb = new StringBuilder();
        sb.AppendLine("# AnyElt Universal Capability Matrix");
        sb.AppendLine();
        sb.AppendLine("> **Auto-generated at build time via runtime reflection across self-declared adapter capabilities.**");
        sb.AppendLine();
        sb.Append("| ELT Platform | ");
        sb.Append(string.Join(" | ", capabilities.Select(c => c.ToString())));
        sb.AppendLine(" |");

        sb.Append("| :--- | ");
        sb.Append(string.Join(" | ", capabilities.Select(_ => ":---:")));
        sb.AppendLine(" |");

        foreach (var a in adapters)
        {
            sb.Append($"| **{a.Name}** (`{a.EltType}`) | ");
            var cells = capabilities.Select(c => a.HasCapability(c) ? "✔" : "-");
            sb.Append(string.Join(" | ", cells));
            sb.AppendLine(" |");
        }

        return sb.ToString();
    }
}
