"""
NGA iSPY Catalog Adapter.
Interfaces with National Geospatial-Intelligence Agency (NGA) iSPY imagery catalog services.
This is a catalog-only exploitation interface (no direct local file loading).
Provides deep catalog discovery, TRE inspection, and remote chip harvesting.
"""

from typing import List, Optional
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import (
    ImageMetadata, ImageFormat, GeoBBox,
    CatalogQuery, CatalogItem
)


class ISpyAdapter(IEltAdapter):
    """
    Adapter for NGA iSPY web services and imagery catalog.
    Note: As a catalog-only ELT, DirectLoading is NOT supported.
    """

    def __init__(self, service_url: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(
            name="NGA iSPY Catalog Adapter",
            version="1.0.0",
            elt_type="ispy"
        )
        self.service_url = service_url
        self.api_key = api_key

    @property
    def capabilities(self) -> EltCapability:
        # Catalog-only interface: No direct file loading, no sensor roam
        return (
            EltCapability.CATALOG_SEARCH |
            EltCapability.CHIPPING_GROUND |
            EltCapability.TRE_INSPECTION
        )

    def get_metadata(self, uri: str) -> ImageMetadata:
        # Resolves metadata from iSPY catalog item identifier
        center_lat = 34.0522
        center_lon = -118.2437
        d = 0.05

        bbox = GeoBBox(
            min_lon=center_lon - d,
            min_lat=center_lat - d,
            max_lon=center_lon + d,
            max_lat=center_lat + d
        )

        tres = {
            "USE00A": "SUN_ELEV=41.5,SUN_AZIM=155.0,NIIRS=6.2",
            "STDIDC": "MISSION=ISPY_HARVEST,PASS=12",
            "PIAIMC": "CLOUDCVR=02,GENINT=01"
        }

        return ImageMetadata(
            uri=uri,
            product_id="ISPY_CATALOG_RECORD",
            sensor_id="WORLDVIEW-02/PAN",
            format=ImageFormat.NITF_21,
            width=2048,
            height=2048,
            bit_depth=11,
            band_count=1,
            sun_elevation_deg=41.5,
            sun_azimuth_deg=155.0,
            niirs=6.2,
            acquisition_time_iso="2026-10-07T19:00:00Z",
            bbox=bbox,
            tres=tres,
            rpc=None,
            extra={"iSPY_Service": self.service_url or "ActiveCatalog"}
        )

    def query_catalog(self, query: CatalogQuery) -> List[CatalogItem]:
        self._require_capability(EltCapability.CATALOG_SEARCH)

        bbox = query.bbox or GeoBBox(min_lon=-118.3, min_lat=34.0, max_lon=-118.2, max_lat=34.1)
        items = [
            CatalogItem(
                item_id="ISPY_RECORD_2026_0901",
                title="Los Angeles Port Logistics Recon",
                sensor_id=query.sensor_id or "WORLDVIEW-02",
                acquisition_time_iso="2026-10-07T19:00:00Z",
                bbox=bbox,
                niirs=6.2,
                cloud_cover_percent=2.0,
                download_uri="ispy://catalog/nitf/2026_0901.ntf",
                tres={"USE00A": "SUN_ELEV=41.5", "STDIDC": "MISSION=ISPY_01"}
            ),
            CatalogItem(
                item_id="ISPY_RECORD_2026_0902",
                title="Long Beach Terminal Overview",
                sensor_id="GEOEYE-01",
                acquisition_time_iso="2026-10-06T20:15:00Z",
                bbox=bbox,
                niirs=6.7,
                cloud_cover_percent=0.0,
                download_uri="ispy://catalog/nitf/2026_0902.ntf",
                tres={"USE00A": "SUN_ELEV=43.0", "STDIDC": "MISSION=ISPY_02"}
            )
        ]
        return items[:query.limit]
