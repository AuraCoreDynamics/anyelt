"""
AnyElt: Universal Electronic Light Table (ELT) Abstraction Library.
Sovereign GEOINT exploitation abstraction across desktop, web, catalog, and scientific ELTs.
"""

from anyelt.capabilities import EltCapability, CAPABILITY_METADATA
from anyelt.models import (
    ImageFormat, DraMode, GeoPoint, PixelPoint, GeoBBox, PixelBBox,
    RpcCoefficients, ImageMetadata, RadiometricParameters, ViewportState,
    ChipRequest, ImageChip, MensurationRequest, MensurationResult,
    CatalogQuery, CatalogItem, SpectralSignature
)
from anyelt.exceptions import (
    AnyEltException, UnsupportedCapabilityException, EltConnectionException,
    ImageNotFoundException, MensurationException, CatalogQueryException,
    BridgingException
)
from anyelt.base import IEltAdapter
from anyelt.bridge import EltBridge, EltSessionBroker
from anyelt.adapters import (
    AuraMistAdapter, SocetGxpAdapter, RemoteViewAdapter,
    QgisAdapter, ISpyAdapter, ImageJAdapter, QuasarAdapter
)
from anyelt.api import (
    get_adapter, get_all_adapters, find_best_elt, open_image,
    bridge, sync_viewports, chip_and_send, mensurate_shadow,
    get_capability_matrix, get_capability_matrix_markdown
)

__version__ = "1.0.0"

__all__ = [
    # Capabilities & Models
    "EltCapability",
    "CAPABILITY_METADATA",
    "ImageFormat",
    "DraMode",
    "GeoPoint",
    "PixelPoint",
    "GeoBBox",
    "PixelBBox",
    "RpcCoefficients",
    "ImageMetadata",
    "RadiometricParameters",
    "ViewportState",
    "ChipRequest",
    "ImageChip",
    "MensurationRequest",
    "MensurationResult",
    "CatalogQuery",
    "CatalogItem",
    "SpectralSignature",

    # Exceptions
    "AnyEltException",
    "UnsupportedCapabilityException",
    "EltConnectionException",
    "ImageNotFoundException",
    "MensurationException",
    "CatalogQueryException",
    "BridgingException",

    # Base & Bridge
    "IEltAdapter",
    "EltBridge",
    "EltSessionBroker",

    # Adapters
    "AuraMistAdapter",
    "SocetGxpAdapter",
    "RemoteViewAdapter",
    "QgisAdapter",
    "ISpyAdapter",
    "ImageJAdapter",
    "QuasarAdapter",

    # API Helpers
    "get_adapter",
    "get_all_adapters",
    "find_best_elt",
    "open_image",
    "bridge",
    "sync_viewports",
    "chip_and_send",
    "mensurate_shadow",
    "get_capability_matrix",
    "get_capability_matrix_markdown"
]
