namespace AnyElt.Adapters;

using AnyElt.Core;
using AnyElt.Extensions;

public class ImageJAdapter : BaseEltAdapter
{
    public string? ImageJPath { get; set; }

    public ImageJAdapter(string? imagejPath = null)
        : base("ImageJ / Fiji GEOINT Adapter", "1.0.0", "imagej")
    {
        ImageJPath = imagejPath;
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
        EltCapability.ScriptingMacro |
        EltCapability.TreInspection;

    public override ImageMetadata GetMetadata(string uri)
    {
        return ImageJGeointExtension.SynthesizeGeointMetadata(uri);
    }

    public string ExecuteMacro(IEnumerable<string> commands)
    {
        RequireCapability(EltCapability.ScriptingMacro);
        return ImageJGeointExtension.GenerateImageJMacro("AnyEltBatchExecution", commands);
    }
}
