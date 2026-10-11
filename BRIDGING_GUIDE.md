# Cross-ELT Bridging Guide

> **Document Identifier:** `AURA-ANYELT-BRIDGE-001`  
> **Authors:** AuraCore Dynamics Engineering  

---

## 1. Why Cross-ELT Bridging?

Analysts frequently work in mixed environments:
- **SOCET GXP** provides rigorous stereo photogrammetry and sensor-space manipulation, but lacks open Python plugin ecosystems.
- **QGIS** provides extensive GIS vector layers, shapefiles, and spatial DB connections, but lacks native RPC00B sensor-space roaming.
- **AuraMist** provides sovereign browser-based collaboration and edge caching, ideal for field deployments.
- **NGA iSPY** holds imagery metadata and dissemination services, but does not render local data.
- **ImageJ / Fiji** has cutting-edge scientific filters, Fourier transforms, and edge detectors, but does not understand NITF TREs out of the box.
- **Quasar (Orange)** provides chemometric spectroscopy analysis on hypercubes, but does not provide map navigation.

**AnyElt Bridging** connects these isolated tools into an integrated exploitation suite.

---

## 2. Common Bridging Recipes

### Recipe 1: Synchronized Dual-Display (SOCET GXP $\to$ QGIS)
Keep an unrectified sensor view in SOCET GXP and an orthorectified map view in QGIS locked in tandem.

```python
import anyelt

gxp = anyelt.get_adapter("socet_gxp")
qgis = anyelt.get_adapter("qgis")
bridge = anyelt.bridge(gxp, qgis)

# When an analyst pans in SOCET GXP:
gxp.roam_to_pixel(x=2048, y=2048, zoom=2.0)

# Synchronize: AnyElt uses GXP's RPC camera model to calculate (lat, lon) and roams QGIS
bridge.sync_viewport()
```

### Recipe 2: Catalog Discovery to Exploitation (iSPY $\to$ AuraMist)
Query a remote defense catalog and immediately mount the best pass into a Web ELT session.

```python
import anyelt
from anyelt.models import CatalogQuery, GeoBBox

ispy = anyelt.get_adapter("ispy")
auramist = anyelt.get_adapter("auramist")
bridge = anyelt.bridge(ispy, auramist)

# Query and load
query = CatalogQuery(
    bbox=GeoBBox(min_lon=-118.3, min_lat=34.0, max_lon=-118.2, max_lat=34.1),
    sensor_id="WORLDVIEW-02",
    min_niirs=6.0
)
item = bridge.search_and_load(query)
print(f"Mounted {item.title} into AuraMist Light Table!")
```

### Recipe 3: Scientific Deep-Dive (AuraMist $\to$ ImageJ)
Extract a sub-pixel chip from AuraMist and push it to ImageJ for scientific filtering.

```python
import anyelt
from anyelt.models import ChipRequest, PixelBBox

auramist = anyelt.get_adapter("auramist")
imagej = anyelt.get_adapter("imagej")
bridge = anyelt.bridge(auramist, imagej)

chip = bridge.transfer_chip(ChipRequest(
    image_uri="nitf://auratiles/dc_recon.ntf",
    sensor_bounds=PixelBBox(min_x=500, min_y=500, max_x=1000, max_y=1000),
    output_format="PNG"
))

# Run ImageJ Macro on the chip
macro = imagej.execute_macro([
    "run('Find Edges');",
    "run('Enhance Contrast', 'saturated=0.4');"
])
```
