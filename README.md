# AnyElt: Universal Electronic Light Table (ELT) Abstraction Library

<p align="center">
  <strong>Single-API Abstraction for Sovereign GEOINT Exploitation Workstations</strong><br>
  <em>Dual-Language Parity across Python 3.10+ (pip) and .NET 10.0 / C# 12 (NuGet & Standalone CLI)</em>
</p>

---

## Overview

**AnyElt** is an open-source GEOINT abstraction library developed by **AuraCore Dynamics**. It provides a single, uniform API to interface with diverse Electronic Light Tables (ELTs), including desktop photogrammetry suites, web-native tables, catalog services, and scientific image analysis tools.

Whether your workstation runs **BAE Systems SOCET GXP**, **Textron Systems RemoteView**, **QGIS**, **AuraMist**, **NGA iSPY**, **ImageJ / Fiji**, or **Quasar (Orange Data Miner)**, AnyElt normalizes image ingestion, sensor/ground roaming, WebGL radiometric shaders, dynamic range adjustment (DRA), precision mensuration, and chipping into a coherent interface.

```
                           +------------------------+
                           |  Synapse-GEOINT / Apps |
                           +-----------+------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
          Python: import anyelt                   C#: using AnyElt.Core;
                   |                                       |
        +----------v---------------------------------------v----------+
        |                  AnyElt Universal Interface                 |
        |  (Direct Loading | Catalog Search | Roam | Mensuration)     |
        +----+-------+---------+--------+--------+--------+--------+--+
             |       |         |        |        |        |        |
             v       v         v        v        v        v        v
         AuraMist  SOCET    Remote-   QGIS     iSPY     ImageJ   Quasar
         (Web ELT)  GXP      View    (PyQGIS) (Catalog)  (GEOINT  (Hyper-
                                                        Extension) spectral)
```

---

## Key Features

1. **Dual-Language Parity**: Identical object models, capabilities, and exceptions in Python (`pip install anyelt`) and .NET 10 (`dotnet add package AnyElt.Core`).
2. **Self-Declaring Capability Matrix**: Every adapter self-declares supported features, generating build-time documentation (`CAPABILITY_MATRIX.md`) and enabling dynamic runtime negotiation.
3. **Open-Source Scientific Extensions**:
   - **ImageJ GEOINT Extension**: Injects MIL-STD-2500C NITF TRE parsing, RPC00B rational polynomial sensor models, and macro automation into ImageJ/Fiji.
   - **Quasar Hyperspectral Extension**: Adds hypercube slicing, spectral angle mapper (SAM), and reflectance curve extraction for GEOINT target classification.
4. **Cross-ELT Bridging**:
   - Synchronize viewports between different ELTs (e.g., SOCET GXP $\to$ QGIS) with automated sensor-to-ground RPC projection.
   - Stream imagery chips extracted from catalog-only tools (iSPY) into exploitation tables (AuraMist, RemoteView).
5. **Tactical Mensuration**:
   - Shadow-to-elevation mensuration ($h = L \times \tan(\theta_{\text{sun}})$).
   - Haversine geodetic 2D and 3D surface distance and azimuth calculation.

---

## Capability Matrix Summary

See the full matrix at [CAPABILITY_MATRIX.md](CAPABILITY_MATRIX.md).

| ELT Platform | Direct Load | Catalog Search | Sensor Roam | Ground Roam | Shadow Mensuration | RPC Projection | Multi-Spectral | Hyperspectral | Viewport Sync |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AuraMist** | ✔ | - | ✔ | ✔ | ✔ | ✔ | - | - | ✔ |
| **SOCET GXP** | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | - | ✔ |
| **RemoteView** | ✔ | - | ✔ | ✔ | ✔ | ✔ | - | - | - |
| **QGIS** | ✔ | - | - | ✔ | - | - | ✔ | - | ✔ |
| **NGA iSPY** | - | ✔ | - | - | - | - | - | - | - |
| **ImageJ** | ✔ | - | ✔ | ✔ | ✔ | ✔ | - | - | - |
| **Quasar** | ✔ | - | - | - | - | - | ✔ | ✔ | - |

---

## Quickstart: Python

```python
import anyelt
from anyelt.capabilities import EltCapability
from anyelt.models import ChipRequest, PixelBBox

# 1. Open an image using AuraMist Web ELT
adapter, meta = anyelt.open_image("nitf://auratiles/dc_recon.ntf", elt_type="auramist")
print(f"Loaded {meta.product_id} with sensor {meta.sensor_id}")

# 2. Roam to coordinates and adjust radiometrics
adapter.roam_to_geo(lat=38.8951, lon=-77.0364, zoom=14.0)
adapter.apply_radiometrics(anyelt.RadiometricParameters(brightness=0.2, contrast=1.3))

# 3. Precision shadow mensuration: h = L * tan(theta_sun)
res = anyelt.mensurate_shadow(adapter, shadow_length_m=20.0, sun_elevation_deg=46.8)
print(f"Calculated Height: {res.calculated_value} {res.unit}")

# 4. Cross-ELT Bridging: Sync viewport from SOCET GXP into QGIS
gxp = anyelt.get_adapter("socet_gxp")
qgis = anyelt.get_adapter("qgis")
bridge = anyelt.bridge(gxp, qgis)
bridge.sync_viewport()
```

---

## Quickstart: C# (.NET 10)

```csharp
using AnyElt.Core;
using AnyElt.Adapters;

// 1. Instantiate adapter and load image
var gxp = new SocetGxpAdapter();
var meta = gxp.LoadImage("file://recon_pass.ntf");

// 2. Query internal GXP Xplorer catalog
var items = gxp.QueryCatalog(new CatalogQuery { SensorId = "GEOEYE-01" });

// 3. Extract sensor-space chip and transfer to ImageJ
var ij = new ImageJAdapter();
var bridge = new EltBridge(gxp, ij);
var chip = bridge.TransferChip(new ChipRequest
{
    ImageUri = meta.Uri,
    SensorBounds = new PixelBBox(100, 100, 356, 356)
});
```

---

## Command-Line Tool (CLI)

AnyElt ships as a standalone CLI tool in both Python and .NET:

```bash
# View the dynamic capability matrix
anyelt matrix

# List all installed adapters
anyelt adapters

# Inspect NITF headers and TREs via an adapter
anyelt inspect imagery/pass1.ntf --elt auramist

# Calculate target elevation from shadow length
anyelt mensurate-shadow 25.5 48.2
```

---

## Testing

- **Python Suite**: Run `python -m pytest tests/python/test_anyelt.py` (15/15 tests passing).
- **.NET 10 Suite**: Run `dotnet test AnyElt.slnx` (12/12 tests passing).

---

## License

Licensed under the [Apache License, Version 2.0](LICENSE).  
Copyright 2026 AuraCore Dynamics.
