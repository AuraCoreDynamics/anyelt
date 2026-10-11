# AnyElt: Universal Electronic Light Table (ELT) Abstraction Library
## Master Engineering Taskgroup Specification

> **Document Identifier:** `AURA-ANYELT-TG-001`  
> **Classification:** AuraCore Dynamics Open Source Engineering  
> **Repository:** `https://github.com/AuraCoreDynamics/anyelt.git`  
> **Local Root:** `c:\projects\auracore\anyelt`  
> **Runtime Baseline:** Python 3.10+ (pip module / PyPI) & .NET 10.0 / C# 12 (NuGet & Standalone CLI / App)  
> **Client Consumer Integration:** Synapse-GEOINT Cognitive Fabric, AuraMist, Disme, AuraVault  

---

## 1. System Vision & Architecture

Electronic Light Tables (ELTs) are the primary tactical and scientific exploitation workstations used in modern GEOINT. However, analysts and automated systems operate across a fragmented spectrum of tools:
- Heavyweight proprietary desktop ELTs (BAE Systems **SOCET GXP**, Textron Systems **RemoteView**).
- Open GIS desktop platforms with raster exploitation plugins (**QGIS**).
- Cloud and sovereign web-native ELTs (**AuraMist**).
- Catalog-centric exploitation services (NGA **iSPY**, GXP Xplorer).
- Open-source scientific image processors lacking standard geospatial models (**ImageJ / Fiji**, **Quasar** on Orange Data Miner).

**AnyElt** bridges this divide by providing:
1. **Unified Dual-Language API**: Idiomatic Python (`import anyelt`) and C# (`using AnyElt.Core;`) APIs presenting a single, standard contract.
2. **Self-Declaring Capability Matrix**: Every adapter dynamically declares its features (`Capabilities.DirectLoading`, `Capabilities.CatalogSearch`, `Capabilities.RadiometricEnhancement`, `Capabilities.MensurationShadow`, `Capabilities.RpcProjection`, `Capabilities.ChippingSensor`, `Capabilities.Hyperspectral`, etc.), powering automated build-time matrix generation and programmatic runtime negotiation.
3. **Open-Source ELT Extensions**: Enhancing scientific tools like ImageJ and Quasar with native NITF TRE parsers, RPC polynomial math, and geospatial coordinate sync, transforming them into full-fledged GEOINT ELTs.
4. **Cross-ELT Bridging & Composition**: Orchestrating multi-tool workflows on a workstation (e.g. querying an iSPY catalog, loading in SOCET GXP, synchronizing viewports with QGIS, and streaming spectral chips to ImageJ or Quasar).
5. **Synapse-GEOINT Bridge**: High-integrity, error-resilient abstraction layer purpose-built for cognitive agents and automated exploitation pipelines.

---

## 2. Execution Taskgroup Topology

```
TG-001: Core Architecture & Dual Contracts (Python & C#)
   │
   ├──► TG-002: AuraMist Web ELT Adapter (REST, WebSocket, AMEPS, AuraTiles)
   ├──► TG-003: BAE Systems SOCET GXP Adapter (GXP Xplorer, REST/CLI automation)
   ├──► TG-004: Textron Systems RemoteView Adapter (Direct load, socket/CLI, mensuration)
   ├──► TG-005: QGIS PyQGIS / RPC Bridge Adapter (Direct raster, PyQGIS, RPC socket)
   ├──► TG-006: NGA iSPY Catalog Adapter (Catalog-only search, REST, remote chip)
   ├──► TG-007: ImageJ / Fiji Extension & Adapter (Scientific processor + AnyElt ELT engine)
   └──► TG-008: Quasar / Orange Hyperspectral Extension & Adapter (Spectral cube analysis)
   │
TG-009: Cross-ELT Bridging Engine & Multi-Tool Orchestration
   │
TG-010: Build-Time Capability Matrix Generator & Programmatic Reflection
   │
TG-011: Convenience Helpers & Unified API Harmonization Pass
   │
TG-012: Full Verification (pytest + xUnit), Packaging (pip + NuGet + CLI), Git Deploy
```

---

## 3. Individual Taskgroup Breakdown

### TG-001: Core Architecture, Dual Contracts & Capability System
- **Objective**: Establish shared core abstractions in Python and C#.
- **Models**:
  - `EltCapabilities`: Bitmask/Enum representing 20+ fine-grained exploitation traits.
  - `ImageMetadata`: Product ID, sensor ID, format (NITF 2.1, GeoTIFF, etc.), dimensions, bit depth, bands, sun elevation/azimuth, acquisition time, bounding box (WGS84), TRE dictionary, RPC coefficients.
  - `ViewportState`: Center lat/lon, center pixel X/Y, zoom level, rotation angle (degrees), dynamic range adjustment settings (DRA).
  - `RadiometricParameters`: Brightness, contrast, gamma, sharpen, invert, DRA mode (Auto 1-99%, Min-Max, Histogram Equalize, Linear).
  - `ChipRequest` & `ImageChip`: Pixel bounds, geodetic bounds, space (Sensor vs Ground), target format (PNG, TIFF, Raw Array), byte payload.
  - `MensurationResult`: Shadow height ($h = L \times \tan(\theta_{sun})$), 2D distance, 3D distance, azimuth, target coordinates.
  - `CatalogQuery` & `CatalogItem`: Spatial bbox, temporal window, sensor filter, NIIRS range, cloud cover max.
- **Interfaces**:
  - Python: `class IEltAdapter(ABC)`
  - C#: `public interface IEltAdapter`
- **Error Hierarchy**:
  - `AnyEltException`, `UnsupportedCapabilityException`, `EltConnectionException`, `ImageNotFoundException`, `MensurationException`.

### TG-002: AuraMist Web ELT Adapter
- **Objective**: Interface with AuraMist sovereign web ELT and AuraTiles backend.
- **Capabilities**: DirectLoading, RadiometricEnhancement, SensorRoam, GroundRoam, MensurationShadow, MensurationDistance, RpcProjection, ChippingSensor, ChippingGround, TreInspection, ViewportSync.
- **Integration**: REST client for AuraMist endpoints, WebSocket live state synchronization, AuraTiles dual-space tiles (`/tiles/nitf/{key}/ortho` and `/sensor`).

### TG-003: BAE Systems SOCET GXP Adapter
- **Objective**: Interface with BAE Systems SOCET GXP and GXP Xplorer catalog.
- **Capabilities**: DirectLoading, CatalogSearch, RadiometricEnhancement, SensorRoam, GroundRoam, MensurationShadow, MensurationDistance, RpcProjection, ChippingSensor, ChippingGround, TreInspection, MultiSpectral, ViewportSync.
- **Integration**: Automation API / CLI bridge / REST Xplorer catalog endpoints, project/workspace management, RPC-guided roam.

### TG-004: Textron Systems RemoteView Adapter
- **Objective**: Interface with Textron Systems RemoteView exploitation environment.
- **Capabilities**: DirectLoading, RadiometricEnhancement, SensorRoam, GroundRoam, MensurationShadow, MensurationDistance, RpcProjection, ChippingSensor, ChippingGround, TreInspection.
- **Integration**: Direct NITF loading, command-line / socket automation interface, sensor-space chipping, shadow mensuration.

### TG-005: QGIS PyQGIS / RPC Bridge Adapter
- **Objective**: Interface with QGIS desktop via PyQGIS / AnyElt QGIS RPC server plugin.
- **Capabilities**: DirectLoading, RadiometricEnhancement, GroundRoam, MensurationDistance, ChippingGround, TreInspection, MultiSpectral, ViewportSync.
- **Integration**: Python PyQGIS direct module binding or background JSON-RPC bridge socket, raster layer addition, canvas extent sync, raster band rendering.

### TG-006: NGA iSPY Catalog Adapter
- **Objective**: Interface with NGA iSPY web services and imagery dissemination catalog.
- **Capabilities**: CatalogSearch, TreInspection, ChippingGround. (Catalog-Only ELT).
- **Integration**: REST query by bbox/time/sensor, metadata harvesting, WCS/WMS tile retrieval, chip cutout generation.

### TG-007: ImageJ / Fiji Extension & Adapter
- **Objective**: Transform open-source scientific image processor ImageJ into a GEOINT ELT.
- **AnyElt Extension**: Built-in geospatial extension providing MIL-STD-2500C NITF TRE parsing, RPC sensor-to-ground coordinates, and spatial viewport sync.
- **Capabilities**: DirectLoading, RadiometricEnhancement, SensorRoam, GroundRoam, ChippingSensor, MensurationShadow, MensurationDistance, RpcProjection, ScriptingMacro.
- **Integration**: ImageJ Macro / headless command interface / Python IPC bridge with geospatial metadata injection.

### TG-008: Quasar / Orange Hyperspectral Extension & Adapter
- **Objective**: Interface with Quasar hyperspectral extension for Orange Data Miner.
- **AnyElt Extension**: Built-in hyperspectral cube processor extracting spectral signatures across $N$ bands for target classification.
- **Capabilities**: DirectLoading, ChippingSensor, MultiSpectral, Hyperspectral, SpectralSignatureExtraction.
- **Integration**: Spectral data cube ingestion, band wavelength slicing, ROI spectral signature extraction, spectral curve comparison.

### TG-009: Cross-ELT Bridging Engine & Multi-Tool Orchestration
- **Objective**: Provide seamless multi-ELT bridging on workstations.
- **Capabilities**: CrossEltBridge, ViewportSync.
- **Workflows**:
  - Coordinate/Viewport mirroring: Roam in SOCET GXP $\to$ syncs AuraMist or QGIS.
  - Catalog-to-Exploitation routing: Search iSPY $\to$ stream image into RemoteView or AuraMist.
  - Multi-spectral offload: Direct chip from SOCET GXP $\to$ send to Quasar or ImageJ for spectral analysis.
  - Fallback negotiation: Query which installed ELT supports a requested capability.

### TG-010: Build-Time Capability Matrix Generator
- **Objective**: Automated reflection across all adapters generating documentation & programmatic lookup.
- **Outputs**:
  - `CAPABILITY_MATRIX.md` (Markdown table)
  - `capabilities.json` (Machine-readable)
  - Programmatic API: `anyelt.get_capability_matrix()` / `EltRegistry.GetCapabilityMatrix()`.

### TG-011: Convenience Helpers & API Harmonization Pass
- **Objective**: Provide an ultra-ergonomic top-level developer experience.
- **Convenience Functions**:
  - `anyelt.open(uri, elt_type=None)`
  - `anyelt.find_best_elt(required_capabilities)`
  - `anyelt.bridge(source_elt, target_elt)`
  - `anyelt.chip_and_send(source_elt, target_elt, bbox)`
  - `anyelt.mensurate_shadow(elt, shadow_length, sun_elevation)`
  - `anyelt.sync_viewports(elts)`

### TG-012: Full Verification, Packaging & Deployment
- **Objective**: Zero-defect testing and packaging.
- **Testing**:
  - Python pytest suite covering all adapters, models, bridging, and matrix generator.
  - .NET 10 xUnit suite covering all C# classes, adapters, bridging, and CLI.
- **Packaging**:
  - Python: `pyproject.toml`, `setup.py` (pip installable, CLI entry point `anyelt`).
  - .NET: `AnyElt.sln`, `src/AnyElt.Cli` (packable as NuGet and standalone executable).
- **Git Deployment**: Clean, production-grade commit and push to `https://github.com/AuraCoreDynamics/anyelt.git`.
