# TG-005: QGIS PyQGIS & RPC Bridge Adapter Integration

> **Taskgroup Identifier:** `AURA-ANYELT-TG-005`  
> **Status:** COMPLETED  
> **Target:** `anyelt/adapters/qgis.py` & `src/AnyElt.Adapters/QgisAdapter.cs`  

## Scope & Implementation
- Integrated with QGIS desktop raster layers via PyQGIS / AnyElt RPC socket bridge.
- Supported Capabilities: `DirectLoading`, `RadiometricEnhancement`, `GroundRoam`, `MensurationDistance`, `ChippingGround`, `TreInspection`, `MultiSpectral`, `ViewportSync`.
- Self-declared lack of `SensorRoam`: correctly throws `UnsupportedCapabilityException` when sensor-space roam is attempted, demonstrating capability negotiation.
