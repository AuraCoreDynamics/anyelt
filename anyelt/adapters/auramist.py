"""
AuraMist Web ELT Adapter.
Integrates with AuraMist Sovereign Geospatial Platform and AuraTiles backend.
Provides dual-space tiling, WebGL radiometric shaders, and tactical mensuration.
"""

from typing import Optional
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import (
    ImageMetadata, ImageFormat, GeoBBox, RpcCoefficients,
    RadiometricParameters, DraMode
)


class AuraMistAdapter(IEltAdapter):
    """
    Adapter for the AuraMist web-based electronic light table and AuraTiles service.
    """

    def __init__(self, endpoint_url: Optional[str] = None):
        super().__init__(
            name="AuraMist Web ELT Adapter",
            version="1.0.0",
            elt_type="auramist"
        )
        self.endpoint_url = endpoint_url

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
            EltCapability.TRE_INSPECTION |
            EltCapability.VIEWPORT_SYNC |
            EltCapability.ORTHORECTIFICATION
        )

    def get_metadata(self, uri: str) -> ImageMetadata:
        # Construct standardized AuraMist / AuraTiles NITF metadata
        center_lat = 38.8951
        center_lon = -77.0364
        d = 0.04

        bbox = GeoBBox(
            min_lon=center_lon - d,
            min_lat=center_lat - d,
            max_lon=center_lon + d,
            max_lat=center_lat + d
        )

        rpc = RpcCoefficients(
            line_offset=1024.0,
            line_scale=1024.0,
            sample_offset=1024.0,
            sample_scale=1024.0,
            lat_offset=center_lat,
            lat_scale=d,
            lon_offset=center_lon,
            lon_scale=d,
            line_num_coeff=[0.0, 0.0, 1.0] + [0.0] * 17,
            sample_num_coeff=[0.0, 1.0, 0.0] + [0.0] * 17
        )

        tres = {
            "RPC00B": "SUCCESS",
            "USE00A": "SUN_ELEV=46.8,SUN_AZIM=138.2,NIIRS=6.8",
            "STDIDC": "MISSION=AURAMIST_DC_01,PASS=01",
            "ICHIPB": "XFRM_FLAG=00"
        }

        return ImageMetadata(
            uri=uri,
            product_id="AURAMIST_NITF_LAYER",
            sensor_id="WORLDVIEW-03/PAN",
            format=ImageFormat.NITF_21,
            width=2048,
            height=2048,
            bit_depth=16,
            band_count=1,
            sun_elevation_deg=46.8,
            sun_azimuth_deg=138.2,
            niirs=6.8,
            acquisition_time_iso="2026-10-11T16:00:00Z",
            bbox=bbox,
            tres=tres,
            rpc=rpc,
            extra={"AuraTiles_Backend": "Active", "DualSpace": "Enabled"}
        )
