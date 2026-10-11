"""
ImageJ / Fiji GEOINT Adapter.
Integrates with the open-source scientific image processor ImageJ / Fiji.
Enhanced with AnyElt's ImageJGeointExtension to provide full GEOINT ELT capabilities:
MIL-STD-2500C NITF TRE parsing, RPC00B rational polynomial sensor models,
and macro script automation.
"""

from typing import Optional, List
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import ImageMetadata
from anyelt.extensions.imagej_geoint import ImageJGeointExtension


class ImageJAdapter(IEltAdapter):
    """
    Adapter for ImageJ / Fiji scientific image processing workstation.
    Equipped with AnyElt GEOINT extension to make it a full-fledged light table.
    """

    def __init__(self, imagej_path: Optional[str] = None):
        super().__init__(
            name="ImageJ / Fiji GEOINT Adapter",
            version="1.0.0",
            elt_type="imagej"
        )
        self.imagej_path = imagej_path

    @property
    def capabilities(self) -> EltCapability:
        # Full-fledged ELT via AnyElt ImageJ Extension
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
            EltCapability.SCRIPTING_MACRO |
            EltCapability.TRE_INSPECTION
        )

    def get_metadata(self, uri: str) -> ImageMetadata:
        # Synthesize full GEOINT metadata via extension
        return ImageJGeointExtension.synthesize_geoint_metadata(uri)

    def execute_macro(self, commands: List[str]) -> str:
        """Execute an ImageJ macro script within the ImageJ runtime."""
        self._require_capability(EltCapability.SCRIPTING_MACRO)
        script = ImageJGeointExtension.generate_imagej_macro("AnyEltBatchExecution", commands)
        return script
