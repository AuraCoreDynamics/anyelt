"""
QGIS Desktop & PyQGIS Bridge Adapter.
Interfaces with QGIS raster layers and canvas via PyQGIS or AnyElt RPC socket.
Provides ground-space navigation, multispectral band styling, and canvas extent sync.
"""

from typing import Optional
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import (
    ImageMetadata, ImageFormat, GeoBBox
)


class QgisAdapter(IEltAdapter):
    """
    Adapter for QGIS desktop and PyQGIS automation.
    """

    def __init__(self, rpc_port: int = 9180):
        super().__init__(
            name="QGIS PyQGIS Bridge Adapter",
            version="1.0.0",
            elt_type="qgis"
        )
        self.rpc_port = rpc_port

    @property
    def capabilities(self) -> EltCapability:
        return (
            EltCapability.DIRECT_LOADING |
            EltCapability.RADIOMETRIC_ENHANCEMENT |
            EltCapability.GROUND_ROAM |
            EltCapability.MENSURATION_DISTANCE |
            EltCapability.CHIPPING_GROUND |
            EltCapability.TRE_INSPECTION |
            EltCapability.MULTI_SPECTRAL |
            EltCapability.VIEWPORT_SYNC
        )

    def get_metadata(self, uri: str) -> ImageMetadata:
        center_lat = 45.4215
        center_lon = -75.6972
        d = 0.08

        bbox = GeoBBox(
            min_lon=center_lon - d,
            min_lat=center_lat - d,
            max_lon=center_lon + d,
            max_lat=center_lat + d
        )

        tres = {
            "GDAL_METADATA": "DRIVER=NITF",
            "STDIDC": "MISSION=QGIS_SAMPLE,PASS=01"
        }

        return ImageMetadata(
            uri=uri,
            product_id="QGIS_RASTER_LAYER",
            sensor_id="SENTINEL-2/MSI",
            format=ImageFormat.GEOTIFF,
            width=3600,
            height=3600,
            bit_depth=16,
            band_count=12,
            sun_elevation_deg=48.0,
            sun_azimuth_deg=150.0,
            niirs=4.5,
            acquisition_time_iso="2026-10-08T15:20:00Z",
            bbox=bbox,
            tres=tres,
            rpc=None,
            extra={"QgisRpcPort": self.rpc_port}
        )
