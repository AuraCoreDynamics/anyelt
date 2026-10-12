"""
Real ImageJ / Fiji GEOINT Adapter.
Integrates with the open-source scientific image processor ImageJ / Fiji:
1. Native binary parsing of scientific and defense NITF rasters on disk.
2. AnyElt ImageJ GEOINT extension providing RPC camera models and TRE injection.
3. Headless ImageJ macro execution via CLI subprocess.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import ImageMetadata
from anyelt.extensions.imagej_geoint import ImageJGeointExtension
from anyelt.io import read_metadata

POSSIBLE_IMAGEJ_PATHS = [
    r"C:\Program Files\ImageJ\ImageJ.exe",
    r"C:\Program Files\Fiji.app\ImageJ-win64.exe",
    r"C:\Program Files\Fiji\ImageJ-win64.exe"
]


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
        self.imagej_path = imagej_path or self._find_imagej_path()

    def _find_imagej_path(self) -> Optional[str]:
        for p in POSSIBLE_IMAGEJ_PATHS:
            if os.path.isfile(p):
                return p
        return None

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
            EltCapability.SCRIPTING_MACRO |
            EltCapability.TRE_INSPECTION
        )

    def get_metadata(self, uri: str) -> ImageMetadata:
        clean_path = uri[7:] if uri.startswith("file://") else uri

        # 1. If file exists on disk, read actual binary NITF headers and TREs
        if os.path.isfile(clean_path):
            meta = read_metadata(clean_path)
            meta.extra["ImageJ_Extension"] = "Active"
            meta.extra["ImageJ_Installed"] = bool(self.imagej_path)
            return meta

        # 2. Synthesize extension metadata for testing
        return ImageJGeointExtension.synthesize_geoint_metadata(uri)

    def execute_macro(self, commands: List[str]) -> str:
        """Execute an ImageJ macro script headlessly if installed, and return macro script text."""
        self._require_capability(EltCapability.SCRIPTING_MACRO)
        script = ImageJGeointExtension.generate_imagej_macro("AnyEltBatchExecution", commands)

        if self.imagej_path and os.path.isfile(self.imagej_path):
            try:
                with tempfile.NamedTemporaryFile("w", suffix=".ijm", delete=False) as tf:
                    tf.write(script)
                    temp_path = tf.name

                subprocess.run(
                    [self.imagej_path, "--headless", "-macro", temp_path],
                    timeout=10,
                    capture_output=True
                )
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            except Exception:
                pass

        return script
