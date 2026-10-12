"""
AnyElt Top-Level Convenience API.
Ergonomic helper functions for developers and Synapse-GEOINT cognitive agents.
Provides unified entry points for opening imagery, bridging ELTs, and mensuration.
"""

from typing import Optional, List, Dict, Any, Union
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import (
    ImageMetadata, ViewportState, MensurationRequest, MensurationResult,
    ChipRequest, ImageChip, CatalogQuery, CatalogItem
)
from anyelt.bridge import EltBridge, EltSessionBroker
from anyelt.matrix import generate_capability_matrix_data, generate_capability_matrix_markdown
from anyelt.adapters import (
    AuraMistAdapter, QgisAdapter
)

ADAPTER_REGISTRY: Dict[str, type] = {
    "auramist": AuraMistAdapter,
    "qgis": QgisAdapter
}


def get_adapter(elt_type: str, **kwargs) -> IEltAdapter:
    """
    Instantiate an ELT adapter by its engine key.
    Supported types: 'auramist', 'qgis'.
    """
    key = elt_type.strip().lower()
    if key not in ADAPTER_REGISTRY:
        raise ValueError(f"Unknown ELT type: '{elt_type}'. Available: {list(ADAPTER_REGISTRY.keys())}")
    return ADAPTER_REGISTRY[key](**kwargs)


def get_all_adapters() -> List[IEltAdapter]:
    """Return initialized instances of all available ELT adapters."""
    return [cls() for cls in ADAPTER_REGISTRY.values()]


def find_best_elt(required_capabilities: EltCapability) -> Optional[IEltAdapter]:
    """
    Search available adapters and return the one best satisfying the required capabilities.
    """
    broker = EltSessionBroker()
    for adapter in get_all_adapters():
        broker.register(adapter)
    return broker.find_best_adapter(required_capabilities)


def open_image(uri: str, elt_type: Optional[str] = None, **kwargs) -> tuple[IEltAdapter, ImageMetadata]:
    """
    Open an image URI using the specified or best suited ELT.
    Returns a tuple of (adapter, metadata).
    """
    if elt_type:
        adapter = get_adapter(elt_type, **kwargs)
    else:
        # Default to AuraMist or QGIS
        adapter = find_best_elt(EltCapability.DIRECT_LOADING) or AuraMistAdapter()

    meta = adapter.load_image(uri)
    return adapter, meta


def bridge(source_elt: IEltAdapter, target_elt: IEltAdapter) -> EltBridge:
    """
    Create a bidirectional or unidirectional bridge between two ELTs.
    """
    return EltBridge(source_elt, target_elt)


def sync_viewports(source_elt: IEltAdapter, target_elt: IEltAdapter) -> ViewportState:
    """
    Synchronize the target ELT's viewport to the current coordinates and zoom of the source ELT.
    """
    b = EltBridge(source_elt, target_elt)
    return b.sync_viewport()


def chip_and_send(source_elt: IEltAdapter, target_elt: IEltAdapter, request: ChipRequest) -> ImageChip:
    """
    Extract an image chip from the source ELT and forward it directly to the target ELT.
    """
    b = EltBridge(source_elt, target_elt)
    return b.transfer_chip(request)


def mensurate_shadow(
    elt: IEltAdapter,
    shadow_length_m: float,
    sun_elevation_deg: Optional[float] = None
) -> MensurationResult:
    """
    Calculate target elevation from measured shadow length.
    Applies formula: h = L * tan(theta_sun).
    """
    req = MensurationRequest(
        image_uri=elt.current_image.uri if elt.current_image else "active_layer",
        calculation_type="SHADOW_HEIGHT",
        shadow_length_m=shadow_length_m,
        sun_elevation_deg=sun_elevation_deg
    )
    return elt.mensurate(req)


def get_capability_matrix() -> Dict[str, Any]:
    """Return the structured capability matrix dictionary."""
    return generate_capability_matrix_data()


def get_capability_matrix_markdown() -> str:
    """Return the formatted Markdown capability matrix table."""
    return generate_capability_matrix_markdown()
