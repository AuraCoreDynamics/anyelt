# TG-007: ImageJ / Fiji GEOINT Extension & Adapter Integration

> **Taskgroup Identifier:** `AURA-ANYELT-TG-007`  
> **Status:** COMPLETED  
> **Target:** `anyelt/extensions/imagej_geoint.py`, `anyelt/adapters/imagej.py`, `src/AnyElt.Extensions/ImageJGeointExtension.cs`, `src/AnyElt.Adapters/ImageJAdapter.cs`  

## Scope & Implementation
- Transforms open-source scientific image processor ImageJ / Fiji into a full-fledged GEOINT ELT.
- AnyElt Extension provides:
  - MIL-STD-2500C NITF TRE parsing (`RPC00B`, `USE00A`, `STDIDC`).
  - Active RPC00B 20-term rational polynomial camera model forward projection.
  - ImageJ Macro Language (`.ijm`) script synthesis for automated contrast enhancement, edge detection, and chipping.
- Supported Capabilities: `DirectLoading`, `RadiometricEnhancement`, `DynamicRangeAdjustment`, `SensorRoam`, `GroundRoam`, `MensurationShadow`, `MensurationDistance`, `RpcProjection`, `ChippingSensor`, `ScriptingMacro`, `TreInspection`.
