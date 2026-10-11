"""
AnyElt Capability System.
Provides fine-grained bitmask enumeration and inspection for ELT features.
Used for build-time matrix generation and programmatic runtime negotiation.
"""

from enum import IntFlag, auto
from typing import Dict, List, Set, Any


class EltCapability(IntFlag):
    """
    Bitmask enumeration representing the functional capabilities of an ELT.
    Adapters self-declare which of these capabilities they support.
    """
    NONE = 0
    DIRECT_LOADING = auto()              # Direct loading of local/remote raster files
    CATALOG_SEARCH = auto()              # Query internal or remote image catalogs
    RADIOMETRIC_ENHANCEMENT = auto()     # Brightness, contrast, gamma, sharpness adjustment
    DYNAMIC_RANGE_ADJUSTMENT = auto()    # 1%-99% DRA, Min-Max, Histogram Equalization
    SENSOR_ROAM = auto()                 # Navigation/panning in native sensor space
    GROUND_ROAM = auto()                 # Navigation/panning in geodetic/ground space
    MENSURATION_SHADOW = auto()          # Calculating target elevation from shadow length
    MENSURATION_DISTANCE = auto()        # Calculating 2D/3D geodetic distances
    RPC_PROJECTION = auto()              # Rational Polynomial Camera (RPC00B) projection
    CHIPPING_SENSOR = auto()             # Extracting chips in native pixel space
    CHIPPING_GROUND = auto()             # Extracting orthorectified geodetic chips
    TRE_INSPECTION = auto()              # Reading and parsing NITF Tagged Record Extensions
    MULTI_SPECTRAL = auto()              # Multi-band false color and band combination
    HYPERSPECTRAL = auto()               # Hyperspectral cube slicing and spectral extraction
    SPECTRAL_SIGNATURE = auto()          # Extracting spectral signature curves across wavelengths
    CROSS_ELT_BRIDGE = auto()            # Forwarding commands or data to/from another ELT
    SCRIPTING_MACRO = auto()             # Executing ELT-native macros or automation scripts
    VIEWPORT_SYNC = auto()               # Synchronizing viewport extents with other ELTs
    ORTHORECTIFICATION = auto()          # On-the-fly orthorectification with DEM

    ALL = (
        DIRECT_LOADING | CATALOG_SEARCH | RADIOMETRIC_ENHANCEMENT |
        DYNAMIC_RANGE_ADJUSTMENT | SENSOR_ROAM | GROUND_ROAM |
        MENSURATION_SHADOW | MENSURATION_DISTANCE | RPC_PROJECTION |
        CHIPPING_SENSOR | CHIPPING_GROUND | TRE_INSPECTION |
        MULTI_SPECTRAL | HYPERSPECTRAL | SPECTRAL_SIGNATURE |
        CROSS_ELT_BRIDGE | SCRIPTING_MACRO | VIEWPORT_SYNC |
        ORTHORECTIFICATION
    )


# Human-friendly descriptions and matrix column headers
CAPABILITY_METADATA: Dict[EltCapability, Dict[str, str]] = {
    EltCapability.DIRECT_LOADING: {
        "name": "Direct Loading",
        "description": "Load raster images directly via file path or stream (NITF, GeoTIFF, etc.)",
        "slug": "direct_loading"
    },
    EltCapability.CATALOG_SEARCH: {
        "name": "Catalog Search",
        "description": "Query image catalog by spatial bbox, temporal range, or sensor",
        "slug": "catalog_search"
    },
    EltCapability.RADIOMETRIC_ENHANCEMENT: {
        "name": "Radiometric Enhancement",
        "description": "Adjust brightness, contrast, gamma, sharpness, and color invert",
        "slug": "radiometric_enhancement"
    },
    EltCapability.DYNAMIC_RANGE_ADJUSTMENT: {
        "name": "DRA Modes",
        "description": "Dynamic Range Adjustment (Auto 1-99%, Min-Max, Histogram Equalize)",
        "slug": "dra_modes"
    },
    EltCapability.SENSOR_ROAM: {
        "name": "Sensor Roam",
        "description": "Navigate and zoom in native unrectified sensor pixel coordinates",
        "slug": "sensor_roam"
    },
    EltCapability.GROUND_ROAM: {
        "name": "Ground Roam",
        "description": "Navigate and zoom in geodetic ground space (WGS84 / Web Mercator)",
        "slug": "ground_roam"
    },
    EltCapability.MENSURATION_SHADOW: {
        "name": "Shadow Mensuration",
        "description": "Calculate object height from measured shadow length and sun elevation",
        "slug": "mensuration_shadow"
    },
    EltCapability.MENSURATION_DISTANCE: {
        "name": "Distance Mensuration",
        "description": "Calculate accurate 2D and 3D surface distances and azimuths",
        "slug": "mensuration_distance"
    },
    EltCapability.RPC_PROJECTION: {
        "name": "RPC Projection",
        "description": "Forward/inverse projection using RPC00B rational polynomials",
        "slug": "rpc_projection"
    },
    EltCapability.CHIPPING_SENSOR: {
        "name": "Sensor Chipping",
        "description": "Extract raw sub-image pixel matrices directly from the sensor image",
        "slug": "chipping_sensor"
    },
    EltCapability.CHIPPING_GROUND: {
        "name": "Ground Chipping",
        "description": "Extract georeferenced orthorectified image chips bounded by coordinates",
        "slug": "chipping_ground"
    },
    EltCapability.TRE_INSPECTION: {
        "name": "TRE Inspection",
        "description": "Parse and inspect MIL-STD-2500 Tagged Record Extensions (RPC00B, USE00A)",
        "slug": "tre_inspection"
    },
    EltCapability.MULTI_SPECTRAL: {
        "name": "Multi-Spectral",
        "description": "Band selection, false-color composite synthesis, and band arithmetic",
        "slug": "multi_spectral"
    },
    EltCapability.HYPERSPECTRAL: {
        "name": "Hyperspectral",
        "description": "Exploit high-dimensional hyperspectral data cubes (50+ spectral bands)",
        "slug": "hyperspectral"
    },
    EltCapability.SPECTRAL_SIGNATURE: {
        "name": "Spectral Signature",
        "description": "Extract reflectance wavelength curves from regions of interest (ROI)",
        "slug": "spectral_signature"
    },
    EltCapability.CROSS_ELT_BRIDGE: {
        "name": "Cross-ELT Bridge",
        "description": "Bridge data, chips, and commands between installed ELT applications",
        "slug": "cross_elt_bridge"
    },
    EltCapability.SCRIPTING_MACRO: {
        "name": "Scripting Macro",
        "description": "Execute native scripts, macros, or plugins within the ELT engine",
        "slug": "scripting_macro"
    },
    EltCapability.VIEWPORT_SYNC: {
        "name": "Viewport Sync",
        "description": "Broadcast and listen to synchronized viewport extents across ELTs",
        "slug": "viewport_sync"
    },
    EltCapability.ORTHORECTIFICATION: {
        "name": "Orthorectification",
        "description": "Orthorectify imagery on the fly using digital elevation models (DEM)",
        "slug": "orthorectification"
    },
}


def capability_to_list(caps: EltCapability) -> List[str]:
    """Convert an EltCapability flag into a list of capability slug names."""
    result: List[str] = []
    for flag, meta in CAPABILITY_METADATA.items():
        if caps & flag:
            result.append(meta["slug"])
    return result


def list_to_capability(slugs: List[str]) -> EltCapability:
    """Convert a list of capability slugs into a composite EltCapability bitmask."""
    slug_map = {meta["slug"]: flag for flag, meta in CAPABILITY_METADATA.items()}
    result = EltCapability.NONE
    for slug in slugs:
        clean = slug.strip().lower()
        if clean in slug_map:
            result |= slug_map[clean]
    return result
