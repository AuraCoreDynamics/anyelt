# AnyElt: Universal Electronic Light Table (ELT) Abstraction Library

<p align="center">
  <strong>Single-API Abstraction for Sovereign GEOINT Exploitation Workstations</strong><br>
  <em>Dual-Language Parity across Python 3.10+ (pip) and .NET 10.0 / C# 12 (NuGet & Standalone CLI)</em>
</p>

---

## Overview

**AnyElt** is an open-source GEOINT abstraction library developed by **AuraCore Dynamics**. It provides a single, uniform API to interface with Electronic Light Tables (ELTs), normalizing binary image ingestion, sensor/ground roaming, WebGL radiometric shaders, dynamic range adjustment (DRA), precision mensuration, and chipping into a coherent interface.

AnyElt provides fully authentic integrations with:
1. **AuraMist Web ELT (`auramist`)**: Live REST and WebSocket interface to the AuraMist Sovereign Geospatial Platform, querying live layer catalogs, streaming dual-space coordinates, and controlling WebGL shader light tables.
2. **QGIS Desktop & PyQGIS (`qgis`)**: Genuine PyQGIS headless runtime execution (`python-qgis-ltr.bat`) for native `QgsRasterLayer` inspection and local TCP bridge canvas steering.

```
                           +------------------------+
                           |  Synapse-GEOINT / Apps |
                           +-----------+------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
          Python: import anyelt                   C#: using AnyElt.Core;
                   |                                       |
         +---------v---------------------------------------v---------+
         |                 AnyElt Universal Interface                |
         |  (Direct Loading | Catalog Search | Roam | Mensuration)   |
         +-------------------+-------------------+-------------------+
                             |                   |
                             v                   v
                         AuraMist              QGIS
                        (Web ELT)            (PyQGIS)
```

---

## Key Features

1. **Dual-Language Parity**: Identical object models, capabilities, and exceptions in Python (`pip install anyelt`) and .NET 10 (`dotnet add package AnyElt.Core`).
2. **Native Binary Raster Ingestion**: Pure C# and Python byte-level parsers for MIL-STD-2500C NITF 2.1/2.0 (`FTITLE`, `USE00A`, `RPC00B`, `STDIDC`) and GeoTIFF without third-party dependencies.
3. **Pure Deflate PNG Chipping Engine**: Directly extracts pixel matrices from binary files on disk and streams valid standard PNG chips with CRC32 verification.
4. **Self-Declaring Capability Matrix**: Every adapter self-declares supported features, generating build-time documentation (`CAPABILITY_MATRIX.md`) and enabling dynamic runtime negotiation.
5. **Cross-ELT Bridging**:
   - Synchronize viewports between AuraMist and QGIS with automated coordinate projection.
   - Extract chips from one ELT and inject into another.
6. **Tactical Mensuration**:
   - Shadow-to-elevation mensuration ($h = L \times \tan(\theta_{\text{sun}})$).
   - Haversine geodetic 2D and 3D surface distance and azimuth calculation.

---

## Capability Matrix Summary

See the full matrix at [CAPABILITY_MATRIX.md](CAPABILITY_MATRIX.md).

| ELT Platform | Direct Load | Catalog Search | Radiometrics | Ground Roam | Sensor Roam | Shadow Mensuration | RPC Model | Viewport Sync |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AuraMist** (`auramist`) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| **QGIS** (`qgis`) | ✔ | - | ✔ | ✔ | - | - | - | ✔ |

---

## Quickstart: Python

```python
import anyelt
from anyelt.models import ChipRequest, PixelBBox

# 1. Open an image using AuraMist Web ELT
adapter, meta = anyelt.open_image("imagery/dc_recon.ntf", elt_type="auramist")
print(f"Loaded {meta.product_id} with sensor {meta.sensor_id}")

# 2. Roam to coordinates and adjust radiometrics
adapter.roam_to_geo(lat=38.8951, lon=-77.0364, zoom=14.0)
adapter.apply_radiometrics(anyelt.RadiometricParameters(brightness=0.2, contrast=1.3))

# 3. Precision shadow mensuration: h = L * tan(theta_sun)
res = anyelt.mensurate_shadow(adapter, shadow_length_m=20.0, sun_elevation_deg=46.8)
print(f"Calculated Height: {res.calculated_value} {res.unit}")

# 4. Cross-ELT Bridging: Sync viewport from AuraMist into QGIS
qgis = anyelt.get_adapter("qgis")
bridge = anyelt.bridge(adapter, qgis)
bridge.sync_viewport()
```

---

## Quickstart: C# (.NET 10)

```csharp
using AnyElt.Core;
using AnyElt.Adapters;

// 1. Instantiate adapter and load binary NITF directly from disk
var auramist = new AuraMistAdapter();
var meta = auramist.LoadImage("C:\\Data\\dc_recon.ntf");

// 2. Extract real PNG chip from disk
var chip = auramist.ExtractChip(new ChipRequest
{
    ImageUri = meta.Uri,
    SensorBounds = new PixelBBox(0, 0, 256, 256),
    OutputFormat = "PNG"
});

// 3. Bridge to QGIS desktop
var qgis = new QgisAdapter();
var bridge = new EltBridge(auramist, qgis);
bridge.SyncViewport();
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

## Repository Structure

```
anyelt/
├── anyelt/               # Python Core Library & Adapters
│   ├── adapters/         # Authentic ELT Adapters (auramist, qgis)
│   ├── io/               # Binary NITF/GeoTIFF reader & PNG encoder
│   ├── capabilities.py   # Self-declaring bitwise flags
│   ├── bridge.py         # Cross-ELT synchronization
│   └── matrix.py         # Build-time capability reflection
├── src/                  # .NET 10 Solution (C# 12)
│   ├── AnyElt.Core/      # Core models, interfaces, binary raster IO
│   ├── AnyElt.Adapters/  # AuraMist & QGIS Adapters
│   └── AnyElt.Cli/       # Standalone .NET Global Tool
├── tests/                # Dual Test Suites (xUnit & pytest)
├── CAPABILITY_MATRIX.md  # Official generated capability matrix
└── pyproject.toml        # pip package configuration
```

---

## License

Apache-2.0 - Developed by AuraCore Dynamics for sovereign defense and geospatial intelligence operations.
