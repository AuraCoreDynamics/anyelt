# TG-009: Cross-ELT Bridging & Multi-Tool Orchestration Engine

> **Taskgroup Identifier:** `AURA-ANYELT-TG-009`  
> **Status:** COMPLETED  
> **Target:** `anyelt/bridge.py` & `src/AnyElt.Core/EltBridge.cs`  

## Scope & Implementation
- Developed `EltBridge` to connect pairs of ELTs:
  - `sync_viewport()`: Synchronizes viewports with automated coordinate space translation (evaluating RPC camera models to map sensor pixels into geodetic ground coordinates when bridging between unrectified and GIS tables).
  - `transfer_chip()`: Extracts image chips from source ELT and mounts/transfers to target ELT.
  - `search_and_load()`: Queries catalog-only ELT (e.g. iSPY) and mounts the result into an exploitation ELT (e.g. AuraMist or RemoteView).
- Developed `EltSessionBroker` to manage multi-ELT workstation sessions:
  - Broadcast geodetic roam across all active ground-capable tables.
  - Dynamic capability scoring and fallback negotiation (`find_best_adapter`).
