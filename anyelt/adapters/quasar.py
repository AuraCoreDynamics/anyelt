"""
Quasar / Orange Hyperspectral Adapter.
Integrates with Quasar spectroscopy extension for Orange Data Miner.
Provides hypercube loading, multi-spectral band synthesis, and ROI spectral signature extraction.
"""

from typing import Optional, List
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import (
    ImageMetadata, ImageFormat, GeoBBox, SpectralSignature, PixelBBox
)
from anyelt.extensions.quasar_spectral import QuasarSpectralExtension


class QuasarAdapter(IEltAdapter):
    """
    Adapter for Orange Data Miner / Quasar hyperspectral spectroscopy engine.
    """

    def __init__(self, workspace_path: Optional[str] = None):
        super().__init__(
            name="Quasar / Orange Hyperspectral Adapter",
            version="1.0.0",
            elt_type="quasar"
        )
        self.workspace_path = workspace_path

    @property
    def capabilities(self) -> EltCapability:
        return (
            EltCapability.DIRECT_LOADING |
            EltCapability.CHIPPING_SENSOR |
            EltCapability.MULTI_SPECTRAL |
            EltCapability.HYPERSPECTRAL |
            EltCapability.SPECTRAL_SIGNATURE
        )

    def get_metadata(self, uri: str) -> ImageMetadata:
        center_lat = 37.7749
        center_lon = -122.4194
        d = 0.05

        bbox = GeoBBox(
            min_lon=center_lon - d,
            min_lat=center_lat - d,
            max_lon=center_lon + d,
            max_lat=center_lat + d
        )

        tres = {
            "QUASAR_HYPERCUBE": "BANDS=224,SPECTRAL_RANGE=380-2500nm",
            "SENSOR": "AVIRIS-CLASS-HYPERSPECTRAL"
        }

        return ImageMetadata(
            uri=uri,
            product_id="QUASAR_HYPERCUBE_DATASET",
            sensor_id="AVIRIS-NG/HYPER",
            format=ImageFormat.HDF5,
            width=1024,
            height=1024,
            bit_depth=16,
            band_count=224,
            sun_elevation_deg=55.0,
            sun_azimuth_deg=160.0,
            niirs=None,
            acquisition_time_iso="2026-09-15T18:00:00Z",
            bbox=bbox,
            tres=tres,
            rpc=None,
            extra={"QuasarSpectroscopy": "Enabled", "WavelengthUnit": "nm"}
        )

    def extract_spectral_signature(self, target_name: str, roi: PixelBBox) -> SpectralSignature:
        """Extract spectral reflectance signature from a specified ROI."""
        self._require_capability(EltCapability.SPECTRAL_SIGNATURE)
        return QuasarSpectralExtension.extract_roi_signature(target_name, roi)

    def compare_spectral_signatures(self, sig_a: SpectralSignature, sig_b: SpectralSignature) -> float:
        """Compare two spectral signatures using Spectral Angle Mapper (SAM) metric."""
        return QuasarSpectralExtension.calculate_spectral_angle(sig_a, sig_b)
