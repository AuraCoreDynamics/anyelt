# TG-011: Convenience Helpers & Unified API Harmonization Pass

> **Taskgroup Identifier:** `AURA-ANYELT-TG-011`  
> **Status:** COMPLETED  
> **Target:** `anyelt/api.py`, `anyelt/__init__.py`, `anyelt/cli.py`, `src/AnyElt.Cli/Program.cs`  

## Scope & Implementation
- Completed harmonization pass ensuring consistent method signatures and naming across Python and C#.
- Top-level convenience functions:
  - `anyelt.open_image(uri, elt_type=None)`
  - `anyelt.get_adapter(elt_type, **kwargs)`
  - `anyelt.find_best_elt(required_capabilities)`
  - `anyelt.bridge(source_elt, target_elt)`
  - `anyelt.sync_viewports(source_elt, target_elt)`
  - `anyelt.chip_and_send(source_elt, target_elt, request)`
  - `anyelt.mensurate_shadow(elt, shadow_length_m, sun_elevation_deg=None)`
- Standalone CLI utilities in Python (`anyelt`) and .NET 10 (`anyelt`).
