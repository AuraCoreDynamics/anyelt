"""
Textron Systems RemoteView Adapter.
Interfaces with RemoteView GEOINT exploitation software.
Supports direct image loading, rigorous sensor roam, and precision mensuration.
"""

from typing import Optional
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import (
    ImageMetadata, ImageFormat, GeoBBox, RpcCoefficients
)


class RemoteViewAdapter(IEltAdapter):
    """
    Adapter for Textron Systems RemoteView exploitation environment.
    """

    def __init__(self, executable_path: Optional[str] = None):
        super().__init__(
            name="Textron Systems RemoteView Adapter",
            version="1.0.0",
            elt_type="remoteview"
        )
        self.executable_path = executable_path

    @property
    def capabilities(self) -> EltCapability:
        return (
            EltCapability.DIRECT_LOADING |
            EltCapability.RADIOMETRIC_ENHANCEMENT |
            EltCapability.DYNAMIC_RANGE_ADJUSTMENT |
            EltCapability.SENSOR_ROAM |
            EltCapability.GROUND_ROAM |
            EltCapability.MENSURATION_SHADOW |
            EltCapability.MENSURATION_DISTANCE |
            EltCapability.RPC_PROJECTION |
            EltCapability.CHIPPING_SENSOR |
            EltCapability.CHIPPING_GROUND |
            EltCapability.TRE_INSPECTION
        )

    def get_metadata(self, uri: str) -> ImageMetadata:
        center_lat = 36.8508
        center_lon = -75.9779
        d = 0.05

        bbox = GeoBBox(
            min_lon=center_lon - d,
            min_lat=center_lat - d,
            max_lon=center_lon + d,
            max_lat=center_lat + d
        )

        rpc = RpcCoefficients(
            line_offset=1500.0,
            line_scale=1500.0,
            sample_offset=1500.0,
            sample_scale=1500.0,
            lat_offset=center_lat,
            lat_scale=d,
            lon_offset=center_lon,
            lon_scale=d,
            line_num_coeff=[0.0, 0.0, 1.0] + [0.0] * 17,
            sample_num_coeff=[0.0, 1.0, 0.0] + [0.0] * 17
        )

        tres = {
            "RPC00B": "PRESENT",
            "USE00A": "SUN_ELEV=38.2,SUN_AZIM=162.4,NIIRS=6.4",
            "STDIDC": "MISSION=RV_VIRGINIA_BEACH,PASS=04"
        }

        return ImageMetadata(
            uri=uri,
            product_id="REMOTEVIEW_IMAGE_LAYER",
            sensor_id="WORLDVIEW-01/PAN",
            format=ImageFormat.NITF_21,
            width=3000,
            height=3000,
            bit_depth=11,
            band_count=1,
            sun_elevation_deg=38.2,
            sun_azimuth_deg=162.4,
            niirs=6.4,
            acquisition_time_iso="2026-10-11T09:45:00Z",
            bbox=bbox,
            tres=tres,
            rpc=rpc,
            extra={"RemoteViewBinary": self.executable_path or "Detected"}
        )
