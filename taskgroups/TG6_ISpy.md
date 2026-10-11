# TG-006: NGA iSPY Catalog Adapter Integration

> **Taskgroup Identifier:** `AURA-ANYELT-TG-006`  
> **Status:** COMPLETED  
> **Target:** `anyelt/adapters/ispy.py` & `src/AnyElt.Adapters/ISpyAdapter.cs`  

## Scope & Implementation
- Integrated with National Geospatial-Intelligence Agency (NGA) iSPY imagery catalog services.
- Supported Capabilities: `CatalogSearch`, `ChippingGround`, `TreInspection`.
- Catalog-Only ELT: Deliberately excludes `DirectLoading`. Enforces that consumers query and retrieve imagery records via catalog search rather than attempting direct file loading.
- Demonstrates AnyElt's capability to bridge catalog-only tools into exploitation tools.
