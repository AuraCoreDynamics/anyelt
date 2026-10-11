# TG-008: Quasar / Orange Hyperspectral Extension & Adapter Integration

> **Taskgroup Identifier:** `AURA-ANYELT-TG-008`  
> **Status:** COMPLETED  
> **Target:** `anyelt/extensions/quasar_spectral.py`, `anyelt/adapters/quasar.py`, `src/AnyElt.Extensions/QuasarSpectralExtension.cs`, `src/AnyElt.Adapters/QuasarAdapter.cs`  

## Scope & Implementation
- Integrates with Quasar spectroscopy extension for Orange Data Miner.
- AnyElt Extension provides:
  - 224-channel AVIRIS-class hypercube data ingestion.
  - Mean spectral reflectance signature extraction across Regions of Interest (ROIs).
  - Material spectral curve modeling (Chlorophyll Red Edge, NIR plateau, water absorption, soil, man-made metals).
  - Spectral Angle Mapper (SAM) metric calculation in radians for target classification.
- Supported Capabilities: `DirectLoading`, `ChippingSensor`, `MultiSpectral`, `Hyperspectral`, `SpectralSignature`.
