"""
AnyElt Base Adapter Interface.
Abstract contract that all ELT integrations must implement.
Provides common capability validation, lifecycle management, and fallback math.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import math

from anyelt.capabilities import EltCapability, CAPABILITY_METADATA
from anyelt.models import (
    ImageMetadata, ViewportState, RadiometricParameters,
    ChipRequest, ImageChip, MensurationRequest, MensurationResult,
    CatalogQuery, CatalogItem, GeoPoint, PixelPoint, GeoBBox, PixelBBox
)
from anyelt.exceptions import (
    UnsupportedCapabilityException, MensurationException, EltConnectionException
)


class IEltAdapter(ABC):
    """
    Abstract Base Class for ELT Adapters.
    Every ELT integration self-declares its capabilities and implements standard exploitation verbs.
    """

    def __init__(self, name: str, version: str, elt_type: str):
        self._name = name
        self._version = version
        self._elt_type = elt_type
        self._connected = False
        self._current_image: Optional[ImageMetadata] = None
        self._viewport: ViewportState = ViewportState()

    @property
    def name(self) -> str:
        """Display name of the adapter (e.g. 'SOCET GXP Adapter')."""
        return self._name

    @property
    def version(self) -> str:
        """Adapter release version."""
        return self._version

    @property
    def elt_type(self) -> str:
        """Normalized ELT engine key (e.g. 'auramist', 'socet_gxp', 'remoteview', 'qgis', 'ispy', 'imagej', 'quasar')."""
        return self._elt_type

    @property
    @abstractmethod
    def capabilities(self) -> EltCapability:
        """Bitmask of capabilities supported by this ELT implementation."""
        pass

    def has_capability(self, cap: EltCapability) -> bool:
        """Check if this adapter supports a given capability flag."""
        return bool(self.capabilities & cap)

    def _require_capability(self, cap: EltCapability) -> None:
        """Raise UnsupportedCapabilityException if the adapter lacks the capability."""
        if not self.has_capability(cap):
            cap_meta = CAPABILITY_METADATA.get(cap, {"name": str(cap)})
            raise UnsupportedCapabilityException(self.name, cap_meta["name"])

    # -------------------------------------------------------------------------
    # Lifecycle & Connection
    # -------------------------------------------------------------------------

    def connect(self, connection_string: Optional[str] = None) -> bool:
        """
        Connect to the target ELT process, socket, API, or workspace.
        Default implementation sets connected state to True.
        """
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from the target ELT and release resources."""
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Return True if currently connected and operational."""
        return self._connected

    # -------------------------------------------------------------------------
    # Image Ingestion & Metadata
    # -------------------------------------------------------------------------

    def load_image(self, uri: str) -> ImageMetadata:
        """Load an image into the ELT workspace."""
        self._require_capability(EltCapability.DIRECT_LOADING)
        meta = self.get_metadata(uri)
        self._current_image = meta
        self._viewport.layer_uri = uri
        if meta.bbox:
            self._viewport.center_geo = GeoPoint(lat=meta.bbox.center_lat, lon=meta.bbox.center_lon)
        self._viewport.center_pixel = PixelPoint(x=meta.width / 2.0, y=meta.height / 2.0)
        return meta

    @abstractmethod
    def get_metadata(self, uri: str) -> ImageMetadata:
        """Retrieve standardized image metadata including TREs and RPC models."""
        pass

    @property
    def current_image(self) -> Optional[ImageMetadata]:
        """Currently loaded active image metadata."""
        return self._current_image

    # -------------------------------------------------------------------------
    # Viewport & Roam Navigation
    # -------------------------------------------------------------------------

    def get_viewport(self) -> ViewportState:
        """Retrieve current viewport state."""
        return self._viewport

    def set_viewport(self, viewport: ViewportState) -> ViewportState:
        """Set viewport coordinates, zoom, rotation, and radiometrics."""
        self._viewport = viewport
        return self._viewport

    def roam_to_geo(self, lat: float, lon: float, zoom: Optional[float] = None) -> ViewportState:
        """Roam/pan the light table to geodetic coordinates (WGS84 lat, lon)."""
        self._require_capability(EltCapability.GROUND_ROAM)
        self._viewport.center_geo = GeoPoint(lat=lat, lon=lon)
        if zoom is not None:
            self._viewport.zoom_level = zoom
        return self._viewport

    def roam_to_pixel(self, x: float, y: float, zoom: Optional[float] = None) -> ViewportState:
        """Roam/pan the light table to native sensor pixel coordinates (sample x, line y)."""
        self._require_capability(EltCapability.SENSOR_ROAM)
        self._viewport.center_pixel = PixelPoint(x=x, y=y)
        if zoom is not None:
            self._viewport.zoom_level = zoom
        return self._viewport

    # -------------------------------------------------------------------------
    # Radiometric Enhancement
    # -------------------------------------------------------------------------

    def apply_radiometrics(self, params: RadiometricParameters) -> RadiometricParameters:
        """Apply brightness, contrast, gamma, sharpness, or DRA stretch."""
        self._require_capability(EltCapability.RADIOMETRIC_ENHANCEMENT)
        self._viewport.radiometrics = params
        return params

    # -------------------------------------------------------------------------
    # Chipping Engine
    # -------------------------------------------------------------------------

    def extract_chip(self, request: ChipRequest) -> ImageChip:
        """Extract an image chip according to sensor or ground bounds."""
        if request.sensor_bounds:
            self._require_capability(EltCapability.CHIPPING_SENSOR)
        elif request.ground_bounds:
            self._require_capability(EltCapability.CHIPPING_GROUND)
        else:
            raise ValueError("ChipRequest must specify either sensor_bounds or ground_bounds.")

        # Default synthetic chip generator if not overridden by subclass
        return self._generate_synthetic_chip(request)

    def _generate_synthetic_chip(self, request: ChipRequest) -> ImageChip:
        """Fallback chip byte synthesis for testing and adapters without binary hooks."""
        w = request.sensor_bounds.width if request.sensor_bounds else 256
        h = request.sensor_bounds.height if request.sensor_bounds else 256
        w = max(1, min(w, 4096))
        h = max(1, min(h, 4096))

        # 1x1 to wxh dummy PNG payload with 8-byte magic header
        png_header = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        body = bytes([128] * 64)
        return ImageChip(
            chip_id=f"chip_{self.elt_type}_{w}x{h}",
            source_uri=request.image_uri,
            width=w,
            height=h,
            format=request.output_format,
            data=png_header + body,
            sensor_bounds=request.sensor_bounds,
            ground_bounds=request.ground_bounds,
            metadata={"adapter": self.name, "bands": request.bands or [1]}
        )

    # -------------------------------------------------------------------------
    # Tactical Mensuration
    # -------------------------------------------------------------------------

    def mensurate(self, request: MensurationRequest) -> MensurationResult:
        """Execute mensuration calculation on the active imagery."""
        calc = request.calculation_type.upper()

        if calc == "SHADOW_HEIGHT":
            self._require_capability(EltCapability.MENSURATION_SHADOW)
            # h = L * tan(theta_sun)
            l = request.shadow_length_m
            theta = request.sun_elevation_deg

            # Fallback to current image sun elevation if not provided
            if theta is None and self._current_image and self._current_image.sun_elevation_deg is not None:
                theta = self._current_image.sun_elevation_deg

            if l is None or theta is None:
                raise MensurationException(
                    "SHADOW_HEIGHT requires both shadow_length_m and sun_elevation_deg",
                    calculation_type="SHADOW_HEIGHT"
                )

            theta_rad = math.radians(theta)
            height_m = l * math.tan(theta_rad)
            return MensurationResult(
                calculated_value=round(height_m, 3),
                unit="meters",
                formula_applied="h = L * tan(theta_sun)",
                confidence_score=0.98,
                details={"shadow_length_m": l, "sun_elevation_deg": theta}
            )

        elif calc in ("DISTANCE_2D", "DISTANCE_3D"):
            self._require_capability(EltCapability.MENSURATION_DISTANCE)
            p_a = request.point_a_geo
            p_b = request.point_b_geo

            if not p_a or not p_b:
                raise MensurationException("DISTANCE requires point_a_geo and point_b_geo", calculation_type=calc)

            # Haversine distance
            r_earth = 6371008.8  # meters
            d_lat = math.radians(p_b.lat - p_a.lat)
            d_lon = math.radians(p_b.lon - p_a.lon)
            lat1 = math.radians(p_a.lat)
            lat2 = math.radians(p_b.lat)

            a = (math.sin(d_lat / 2.0) ** 2 +
                 math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2.0) ** 2)
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
            d_2d = r_earth * c

            if calc == "DISTANCE_3D":
                dz = p_b.alt_m - p_a.alt_m
                dist = math.sqrt(d_2d ** 2 + dz ** 2)
            else:
                dist = d_2d

            return MensurationResult(
                calculated_value=round(dist, 3),
                unit="meters",
                formula_applied="Haversine Spherical Surface Geodesic" if calc == "DISTANCE_2D" else "3D Euclidean Geodesic",
                confidence_score=0.99,
                details={"point_a": p_a.to_dict(), "point_b": p_b.to_dict()}
            )

        elif calc == "AZIMUTH":
            self._require_capability(EltCapability.MENSURATION_DISTANCE)
            p_a = request.point_a_geo
            p_b = request.point_b_geo
            if not p_a or not p_b:
                raise MensurationException("AZIMUTH requires point_a_geo and point_b_geo", calculation_type="AZIMUTH")

            lat1 = math.radians(p_a.lat)
            lat2 = math.radians(p_b.lat)
            d_lon = math.radians(p_b.lon - p_a.lon)

            y = math.sin(d_lon) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
            azimuth_deg = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

            return MensurationResult(
                calculated_value=round(azimuth_deg, 2),
                unit="degrees",
                formula_applied="Forward Geodetic Azimuth",
                confidence_score=1.0,
                details={"point_a": p_a.to_dict(), "point_b": p_b.to_dict()}
            )

        else:
            raise MensurationException(f"Unsupported calculation_type: {calc}", calculation_type=calc)

    # -------------------------------------------------------------------------
    # Catalog Search
    # -------------------------------------------------------------------------

    def query_catalog(self, query: CatalogQuery) -> List[CatalogItem]:
        """Search internal or federated imagery catalog."""
        self._require_capability(EltCapability.CATALOG_SEARCH)
        return []

    # -------------------------------------------------------------------------
    # RPC & Geodetic Projections
    # -------------------------------------------------------------------------

    def project_pixel_to_ground(self, uri: str, pixel: PixelPoint) -> GeoPoint:
        """Map sensor pixel (x, y) to geodetic (lat, lon)."""
        self._require_capability(EltCapability.RPC_PROJECTION)
        meta = self.get_metadata(uri)
        if meta.bbox:
            # Linear approximation bounded by BBox if RPC inverse is not loaded
            norm_x = pixel.x / max(1, meta.width)
            norm_y = pixel.y / max(1, meta.height)
            lon = meta.bbox.min_lon + norm_x * (meta.bbox.max_lon - meta.bbox.min_lon)
            lat = meta.bbox.max_lat - norm_y * (meta.bbox.max_lat - meta.bbox.min_lat)
            return GeoPoint(lat=lat, lon=lon)
        return GeoPoint(lat=0.0, lon=0.0)

    def project_ground_to_pixel(self, uri: str, geo: GeoPoint) -> PixelPoint:
        """Map geodetic (lat, lon) to sensor pixel (x, y)."""
        self._require_capability(EltCapability.RPC_PROJECTION)
        meta = self.get_metadata(uri)
        if meta.rpc:
            return meta.rpc.evaluate_forward(geo.lat, geo.lon, geo.alt_m)
        elif meta.bbox:
            # BBox linear interpolation fallback
            norm_lon = (geo.lon - meta.bbox.min_lon) / max(0.000001, (meta.bbox.max_lon - meta.bbox.min_lon))
            norm_lat = (meta.bbox.max_lat - geo.lat) / max(0.000001, (meta.bbox.max_lat - meta.bbox.min_lat))
            return PixelPoint(x=norm_lon * meta.width, y=norm_lat * meta.height)
        return PixelPoint(x=0.0, y=0.0)
