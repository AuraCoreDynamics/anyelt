"""
AnyElt Core Domain Models.
Strictly typed dataclasses representing imagery, viewports, radiometrics,
chips, mensuration results, and catalog items.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import math
import json


class ImageFormat(str, Enum):
    NITF_21 = "NITF_21"
    NITF_20 = "NITF_20"
    GEOTIFF = "GEOTIFF"
    CIB_CADRG = "CIB_CADRG"
    HDF5 = "HDF5"
    ENVI = "ENVI"
    MRF = "MRF"
    JPEG2000 = "JPEG2000"
    PNG = "PNG"
    UNKNOWN = "UNKNOWN"


class DraMode(str, Enum):
    NONE = "NONE"
    AUTO_PERCENTILE = "AUTO_PERCENTILE"      # 1% to 99% cumulative clip
    MIN_MAX = "MIN_MAX"                      # Absolute min-to-max linear stretch
    HISTOGRAM_EQUALIZATION = "HISTOGRAM_EQUALIZATION"
    LINEAR = "LINEAR"


@dataclass
class GeoPoint:
    lat: float
    lon: float
    alt_m: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PixelPoint:
    x: float
    y: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GeoBBox:
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    @property
    def center_lon(self) -> float:
        return (self.min_lon + self.max_lon) / 2.0

    @property
    def center_lat(self) -> float:
        return (self.min_lat + self.max_lat) / 2.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PixelBBox:
    min_x: int
    min_y: int
    max_x: int
    max_y: int

    @property
    def width(self) -> int:
        return max(0, self.max_x - self.min_x)

    @property
    def height(self) -> int:
        return max(0, self.max_y - self.min_y)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RpcCoefficients:
    """
    MIL-STD-2500C RPC00B Rational Polynomial Camera Model Coefficients.
    Maps geodetic coordinates (lat, lon, height) to sensor coordinates (line, sample).
    """
    line_offset: float = 0.0
    line_scale: float = 1.0
    sample_offset: float = 0.0
    sample_scale: float = 1.0
    lat_offset: float = 0.0
    lat_scale: float = 1.0
    lon_offset: float = 0.0
    lon_scale: float = 1.0
    height_offset: float = 0.0
    height_scale: float = 1.0

    # 20-term rational polynomial coefficients
    line_num_coeff: List[float] = field(default_factory=lambda: [0.0] * 20)
    line_den_coeff: List[float] = field(default_factory=lambda: [1.0] + [0.0] * 19)
    sample_num_coeff: List[float] = field(default_factory=lambda: [0.0] * 20)
    sample_den_coeff: List[float] = field(default_factory=lambda: [1.0] + [0.0] * 19)

    def evaluate_forward(self, lat: float, lon: float, height: float = 0.0) -> PixelPoint:
        """Forward projection: (lat, lon, height) -> (sample/x, line/y) in pixel space."""
        # Normalized coordinates [-1.0, 1.0]
        n_lat = (lat - self.lat_offset) / self.lat_scale if self.lat_scale != 0 else 0.0
        n_lon = (lon - self.lon_offset) / self.lon_scale if self.lon_scale != 0 else 0.0
        n_hgt = (height - self.height_offset) / self.height_scale if self.height_scale != 0 else 0.0

        # Monomial basis vector for 20-term cubic polynomial
        u = [
            1.0, n_lon, n_lat, n_hgt, n_lon * n_lat, n_lon * n_hgt, n_lat * n_hgt,
            n_lon ** 2, n_lat ** 2, n_hgt ** 2, n_lon * n_lat * n_hgt,
            n_lon ** 3, n_lon * (n_lat ** 2), n_lon * (n_hgt ** 2),
            (n_lon ** 2) * n_lat, n_lat ** 3, n_lat * (n_hgt ** 2),
            (n_lon ** 2) * n_hgt, (n_lat ** 2) * n_hgt, n_hgt ** 3
        ]

        def poly_val(coeffs: List[float]) -> float:
            return sum(c * val for c, val in zip(coeffs, u))

        line_num = poly_val(self.line_num_coeff)
        line_den = poly_val(self.line_den_coeff)
        sample_num = poly_val(self.sample_num_coeff)
        sample_den = poly_val(self.sample_den_coeff)

        n_line = line_num / line_den if line_den != 0 else 0.0
        n_sample = sample_num / sample_den if sample_den != 0 else 0.0

        line = n_line * self.line_scale + self.line_offset
        sample = n_sample * self.sample_scale + self.sample_offset

        return PixelPoint(x=sample, y=line)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImageMetadata:
    uri: str
    product_id: str
    sensor_id: str
    format: ImageFormat
    width: int
    height: int
    bit_depth: int = 8
    band_count: int = 1
    sun_elevation_deg: Optional[float] = None
    sun_azimuth_deg: Optional[float] = None
    niirs: Optional[float] = None
    acquisition_time_iso: Optional[str] = None
    bbox: Optional[GeoBBox] = None
    tres: Dict[str, str] = field(default_factory=dict)
    rpc: Optional[RpcCoefficients] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["format"] = self.format.value
        return d


@dataclass
class RadiometricParameters:
    brightness: float = 0.0       # Range [-1.0, 1.0], default 0.0
    contrast: float = 1.0         # Range [0.1, 5.0], default 1.0
    gamma: float = 1.0            # Range [0.2, 3.0], default 1.0
    sharpen: float = 0.0          # Range [0.0, 2.0], default 0.0
    invert: bool = False
    dra_mode: DraMode = DraMode.AUTO_PERCENTILE

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["dra_mode"] = self.dra_mode.value
        return d


@dataclass
class ViewportState:
    center_geo: Optional[GeoPoint] = None
    center_pixel: Optional[PixelPoint] = None
    zoom_level: float = 1.0
    rotation_deg: float = 0.0
    radiometrics: RadiometricParameters = field(default_factory=RadiometricParameters)
    layer_uri: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChipRequest:
    image_uri: str
    sensor_bounds: Optional[PixelBBox] = None
    ground_bounds: Optional[GeoBBox] = None
    output_format: str = "PNG"
    bands: Optional[List[int]] = None
    radiometrics: Optional[RadiometricParameters] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImageChip:
    chip_id: str
    source_uri: str
    width: int
    height: int
    format: str
    data: bytes
    sensor_bounds: Optional[PixelBBox] = None
    ground_bounds: Optional[GeoBBox] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["data_size_bytes"] = len(self.data)
        del d["data"]
        return d


@dataclass
class MensurationRequest:
    image_uri: str
    calculation_type: str  # "SHADOW_HEIGHT", "DISTANCE_2D", "DISTANCE_3D", "AZIMUTH"
    point_a_pixel: Optional[PixelPoint] = None
    point_b_pixel: Optional[PixelPoint] = None
    point_a_geo: Optional[GeoPoint] = None
    point_b_geo: Optional[GeoPoint] = None
    shadow_length_m: Optional[float] = None
    sun_elevation_deg: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MensurationResult:
    calculated_value: float
    unit: str
    formula_applied: str
    confidence_score: float = 1.0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CatalogQuery:
    bbox: Optional[GeoBBox] = None
    sensor_id: Optional[str] = None
    start_time_iso: Optional[str] = None
    end_time_iso: Optional[str] = None
    min_niirs: Optional[float] = None
    max_cloud_cover_percent: Optional[float] = None
    limit: int = 50

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CatalogItem:
    item_id: str
    title: str
    sensor_id: str
    acquisition_time_iso: str
    bbox: GeoBBox
    niirs: Optional[float] = None
    cloud_cover_percent: Optional[float] = None
    download_uri: Optional[str] = None
    thumbnail_uri: Optional[str] = None
    tres: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SpectralSignature:
    target_name: str
    wavelengths_nm: List[float]
    reflectance_values: List[float]
    roi_bounds: Optional[PixelBBox] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
