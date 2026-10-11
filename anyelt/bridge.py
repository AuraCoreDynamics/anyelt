"""
AnyElt Cross-ELT Bridging Engine.
Enables orchestration, synchronization, and data/chip routing across multiple ELTs on a workstation.
Supports:
- Viewport mirroring with coordinate space translation (Sensor <-> Ground via RPC)
- Chip extraction and offload between exploitation and scientific engines (e.g. SOCET GXP -> ImageJ)
- Catalog-to-Exploitation automated handoff (e.g. iSPY -> RemoteView / AuraMist)
- Multi-ELT broadcast roaming and session management
"""

from typing import List, Dict, Optional, Any
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import (
    ViewportState, ChipRequest, ImageChip, PixelBBox, GeoBBox,
    CatalogQuery, CatalogItem, SpectralSignature
)
from anyelt.exceptions import BridgingException, UnsupportedCapabilityException


class EltBridge:
    """
    Direct bridge between a source ELT and a target ELT.
    """

    def __init__(self, source_elt: IEltAdapter, target_elt: IEltAdapter):
        self.source = source_elt
        self.target = target_elt

    def sync_viewport(self) -> ViewportState:
        """
        Synchronize the target ELT's viewport to match the source ELT.
        Automatically performs coordinate space translation if necessary:
        - If source is at a geodetic center, roams target to ground coords.
        - If source is in sensor pixel space and target only supports ground space,
          projects the pixel coordinate via RPC/BBox into geodetic coords.
        """
        src_vp = self.source.get_viewport()

        # Target supports Ground Roam
        if self.target.has_capability(EltCapability.GROUND_ROAM):
            if src_vp.center_geo:
                return self.target.roam_to_geo(
                    lat=src_vp.center_geo.lat,
                    lon=src_vp.center_geo.lon,
                    zoom=src_vp.zoom_level
                )
            elif src_vp.center_pixel and self.source.current_image:
                # Coordinate projection from sensor to ground
                try:
                    geo = self.source.project_pixel_to_ground(
                        self.source.current_image.uri,
                        src_vp.center_pixel
                    )
                    return self.target.roam_to_geo(lat=geo.lat, lon=geo.lon, zoom=src_vp.zoom_level)
                except Exception as err:
                    raise BridgingException(self.source.name, self.target.name, f"Coordinate projection failed during sync: {err}")

        # Target supports Sensor Roam
        if self.target.has_capability(EltCapability.SENSOR_ROAM) and src_vp.center_pixel:
            return self.target.roam_to_pixel(
                x=src_vp.center_pixel.x,
                y=src_vp.center_pixel.y,
                zoom=src_vp.zoom_level
            )

        raise BridgingException(
            self.source.name,
            self.target.name,
            "Target ELT does not support compatible navigation space for viewport sync."
        )

    def transfer_chip(self, request: ChipRequest) -> ImageChip:
        """
        Extract an image chip from the source ELT and transfer/load it into the target ELT.
        """
        chip = self.source.extract_chip(request)

        # If target supports direct loading, load the chip URI
        if self.target.has_capability(EltCapability.DIRECT_LOADING):
            try:
                self.target.load_image(chip.source_uri)
            except Exception:
                # Non-fatal if target just receives the binary chip in-memory
                pass

        return chip

    def search_and_load(self, query: CatalogQuery) -> CatalogItem:
        """
        Search catalog in source ELT (e.g. iSPY or GXP Xplorer) and load the best matching
        result into the target exploitation ELT (e.g. AuraMist, RemoteView, SOCET GXP).
        """
        if not self.source.has_capability(EltCapability.CATALOG_SEARCH):
            raise BridgingException(self.source.name, self.target.name, "Source ELT does not support Catalog Search.")

        if not self.target.has_capability(EltCapability.DIRECT_LOADING):
            raise BridgingException(self.source.name, self.target.name, "Target ELT does not support Direct Loading.")

        items = self.source.query_catalog(query)
        if not items:
            raise BridgingException(self.source.name, self.target.name, "No catalog items matched query.")

        selected = items[0]
        load_uri = selected.download_uri or f"catalog://{selected.item_id}"
        self.target.load_image(load_uri)
        return selected


class EltSessionBroker:
    """
    Manages a workstation session with multiple active ELTs.
    Dispatches multi-tool broadcasts, capability routing, and fallback negotiations.
    """

    def __init__(self):
        self._adapters: Dict[str, IEltAdapter] = {}

    def register(self, adapter: IEltAdapter) -> None:
        """Register an active ELT adapter in the workstation session."""
        self._adapters[adapter.elt_type] = adapter

    def get(self, elt_type: str) -> Optional[IEltAdapter]:
        """Get an adapter by key."""
        return self._adapters.get(elt_type)

    @property
    def registered_adapters(self) -> List[IEltAdapter]:
        return list(self._adapters.values())

    def broadcast_roam_geo(self, lat: float, lon: float, zoom: Optional[float] = None) -> Dict[str, ViewportState]:
        """
        Broadcast geodetic roam command to all registered ELTs supporting GROUND_ROAM.
        """
        results: Dict[str, ViewportState] = {}
        for key, adapter in self._adapters.items():
            if adapter.has_capability(EltCapability.GROUND_ROAM):
                try:
                    vp = adapter.roam_to_geo(lat, lon, zoom)
                    results[key] = vp
                except Exception as err:
                    pass
        return results

    def find_best_adapter(self, required_capabilities: EltCapability) -> Optional[IEltAdapter]:
        """
        Find the registered adapter that matches the required capabilities.
        Scores candidate adapters by how many total capabilities they offer.
        """
        candidates = [
            a for a in self._adapters.values()
            if (a.capabilities & required_capabilities) == required_capabilities
        ]
        if not candidates:
            return None
        # Return adapter with maximum capability flags (most feature-rich)
        candidates.sort(key=lambda a: bin(int(a.capabilities)).count("1"), reverse=True)
        return candidates[0]
