# TG-003: BAE Systems SOCET GXP Adapter Integration

> **Taskgroup Identifier:** `AURA-ANYELT-TG-003`  
> **Status:** COMPLETED  
> **Target:** `anyelt/adapters/socet_gxp.py` & `src/AnyElt.Adapters/SocetGxpAdapter.cs`  

## Scope & Implementation
- Integrated with BAE Systems SOCET GXP photogrammetry platform and GXP Xplorer catalog.
- Supported Capabilities: `DirectLoading`, `CatalogSearch`, `RadiometricEnhancement`, `DynamicRangeAdjustment`, `SensorRoam`, `GroundRoam`, `MensurationShadow`, `MensurationDistance`, `RpcProjection`, `ChippingSensor`, `ChippingGround`, `TreInspection`, `MultiSpectral`, `ViewportSync`.
- GXP Xplorer catalog search by spatial bbox, temporal window, and sensor.
- Multispectral 4-band exploitation and RPC camera model handling.
