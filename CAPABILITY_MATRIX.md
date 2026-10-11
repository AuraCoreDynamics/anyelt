# AnyElt Universal Capability Matrix

> **Auto-generated at build time via runtime reflection across self-declared adapter capabilities.**
> This matrix governs runtime capability negotiation, Synapse-GEOINT routing, and cross-ELT fallback selection.

| ELT Platform | Direct Loading | Catalog Search | Radiometric Enhancement | DRA Modes | Sensor Roam | Ground Roam | Shadow Mensuration | Distance Mensuration | RPC Projection | Sensor Chipping | Ground Chipping | TRE Inspection | Multi-Spectral | Hyperspectral | Spectral Signature | Scripting Macro | Viewport Sync | Orthorectification |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AuraMist Web ELT Adapter** (`auramist`) | ✔ | - | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | - | - | - | - | ✔ | ✔ |
| **BAE Systems SOCET GXP Adapter** (`socet_gxp`) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | - | - | - | ✔ | - |
| **Textron Systems RemoteView Adapter** (`remoteview`) | ✔ | - | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | - | - | - | - | - | - |
| **QGIS PyQGIS Bridge Adapter** (`qgis`) | ✔ | - | ✔ | - | - | ✔ | - | ✔ | - | - | ✔ | ✔ | ✔ | - | - | - | ✔ | - |
| **NGA iSPY Catalog Adapter** (`ispy`) | - | ✔ | - | - | - | - | - | - | - | - | ✔ | ✔ | - | - | - | - | - | - |
| **ImageJ / Fiji GEOINT Adapter** (`imagej`) | ✔ | - | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | - | ✔ | - | - | - | ✔ | - | - |
| **Quasar / Orange Hyperspectral Adapter** (`quasar`) | ✔ | - | - | - | - | - | - | - | - | ✔ | - | - | ✔ | ✔ | ✔ | - | - | - |

## Feature Definitions

- **Direct Loading** (`direct_loading`): Load raster images directly via file path or stream (NITF, GeoTIFF, etc.)
- **Catalog Search** (`catalog_search`): Query image catalog by spatial bbox, temporal range, or sensor
- **Radiometric Enhancement** (`radiometric_enhancement`): Adjust brightness, contrast, gamma, sharpness, and color invert
- **DRA Modes** (`dra_modes`): Dynamic Range Adjustment (Auto 1-99%, Min-Max, Histogram Equalize)
- **Sensor Roam** (`sensor_roam`): Navigate and zoom in native unrectified sensor pixel coordinates
- **Ground Roam** (`ground_roam`): Navigate and zoom in geodetic ground space (WGS84 / Web Mercator)
- **Shadow Mensuration** (`mensuration_shadow`): Calculate object height from measured shadow length and sun elevation
- **Distance Mensuration** (`mensuration_distance`): Calculate accurate 2D and 3D surface distances and azimuths
- **RPC Projection** (`rpc_projection`): Forward/inverse projection using RPC00B rational polynomials
- **Sensor Chipping** (`chipping_sensor`): Extract raw sub-image pixel matrices directly from the sensor image
- **Ground Chipping** (`chipping_ground`): Extract georeferenced orthorectified image chips bounded by coordinates
- **TRE Inspection** (`tre_inspection`): Parse and inspect MIL-STD-2500 Tagged Record Extensions (RPC00B, USE00A)
- **Multi-Spectral** (`multi_spectral`): Band selection, false-color composite synthesis, and band arithmetic
- **Hyperspectral** (`hyperspectral`): Exploit high-dimensional hyperspectral data cubes (50+ spectral bands)
- **Spectral Signature** (`spectral_signature`): Extract reflectance wavelength curves from regions of interest (ROI)
- **Scripting Macro** (`scripting_macro`): Execute native scripts, macros, or plugins within the ELT engine
- **Viewport Sync** (`viewport_sync`): Broadcast and listen to synchronized viewport extents across ELTs
- **Orthorectification** (`orthorectification`): Orthorectify imagery on the fly using digital elevation models (DEM)