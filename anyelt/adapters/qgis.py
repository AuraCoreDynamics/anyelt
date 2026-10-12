"""
Real QGIS Desktop & PyQGIS Bridge Adapter.
Interfaces with QGIS raster layers and canvas:
1. Native QgsRasterLayer inspection via headless PyQGIS (python-qgis-ltr.bat).
2. Direct binary metadata extraction via anyelt.io.read_metadata.
3. Socket IPC bridge to command live QGIS GUI extents.
"""

import os
import subprocess
import json
import socket
from pathlib import Path
from typing import Optional, Dict, Any

from anyelt.base import IEltAdapter
from anyelt.capabilities import EltCapability
from anyelt.models import ImageMetadata, ImageFormat, GeoBBox, ViewportState
from anyelt.exceptions import ImageNotFoundException
from anyelt.io import read_metadata

POSSIBLE_QGIS_BATCH_PATHS = [
    r"C:\Program Files\QGIS 3.40.8\bin\python-qgis-ltr.bat",
    r"C:\Program Files\QGIS 3.34\bin\python-qgis-ltr.bat",
    r"C:\Program Files\QGIS\bin\python-qgis.bat"
]


class QgisAdapter(IEltAdapter):
    """
    Adapter for QGIS desktop and PyQGIS automation.
    """

    def __init__(self, rpc_port: int = 9180, qgis_batch_path: Optional[str] = None):
        super().__init__(
            name="QGIS PyQGIS Bridge Adapter",
            version="1.0.0",
            elt_type="qgis"
        )
        self.rpc_port = rpc_port
        self.qgis_batch_path = qgis_batch_path or self._find_qgis_batch()
        self._sock: Optional[socket.socket] = None

    def _find_qgis_batch(self) -> Optional[str]:
        for p in POSSIBLE_QGIS_BATCH_PATHS:
            if os.path.isfile(p):
                return p
        return None

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

    def connect(self, connection_string: Optional[str] = None) -> bool:
        super().connect(connection_string)
        # Attempt connecting to live QGIS GUI socket bridge
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect(("sm", self.rpc_port))
            self._sock = s
        except Exception:
            self._sock = None
        return True

    def disconnect(self) -> None:
        super().disconnect()
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def get_metadata(self, uri: str) -> ImageMetadata:
        clean_path = uri[7:] if uri.startswith("file://") else uri

        # 1. If file exists on disk and PyQGIS is available, query real QgsRasterLayer
        if os.path.isfile(clean_path) and self.qgis_batch_path and os.path.isfile(self.qgis_batch_path):
            py_meta = self._query_via_pyqgis(clean_path)
            if py_meta:
                return py_meta

        # 2. Direct binary inspection via anyelt.io
        if os.path.isfile(clean_path):
            meta = read_metadata(clean_path)
            meta.extra["QgisEngine"] = "Native_RasterReader"
            return meta

        raise ImageNotFoundException(f"Raster file '{uri}' not found on disk.")

    def roam_to_geo(self, lat: float, lon: float, zoom: Optional[float] = None) -> ViewportState:
        vp = super().roam_to_geo(lat, lon, zoom)

        # If connected to live QGIS socket bridge, set canvas extent
        if self._sock:
            try:
                span = 0.05 / (zoom or 1.0)
                cmd = json.dumps({
                    "cmd": "set_extent",
                    "min_x": lon - span,
                    "min_y": lat - span,
                    "max_x": lon + span,
                    "max_y": lat + span
                }) + "\n"
                self._sock.sendall(cmd.encode("utf-8"))
            except Exception:
                pass

        return vp

    def _query_via_pyqgis(self, file_path: str) -> Optional[ImageMetadata]:
        try:
            escaped_path = file_path.replace("\\", "/")
            qgis_prefix = str(Path(self.qgis_batch_path).parent.parent / "apps" / "qgis-ltr")
            script = f"""
import sys, json
from qgis.core import QgsApplication, QgsRasterLayer
QgsApplication.setPrefixPath(r'{qgis_prefix}', True)
qgs = QgsApplication([], False)
qgs.initQgis()
layer = QgsRasterLayer('{escaped_path}', 'Layer')
if layer.isValid():
    ext = layer.extent()
    res = {{
        'valid': True,
        'width': layer.width(),
        'height': layer.height(),
        'bands': layer.bandCount(),
        'crs': layer.crs().authid(),
        'bbox': [ext.xMinimum(), ext.yMinimum(), ext.xMaximum(), ext.yMaximum()]
    }}
else:
    res = {{'valid': False}}
print('__QGIS_OUT__' + json.dumps(res))
qgs.exitQgis()
"""
            compact_script = " ".join([line.strip() for line in script.splitlines() if line.strip()])
            res = subprocess.run(
                [self.qgis_batch_path, "-c", compact_script],
                capture_output=True,
                text=True,
                timeout=8
            )

            if "__QGIS_OUT__" in res.stdout:
                marker = res.stdout.index("__QGIS_OUT__")
                payload = json.loads(res.stdout[marker + len("__QGIS_OUT__"):].strip())
                if payload.get("valid"):
                    w = payload["width"]
                    h = payload["height"]
                    bands = payload["bands"]
                    crs = payload["crs"]
                    bbox_list = payload["bbox"]

                    fmt = ImageFormat.NITF_21 if file_path.lower().endswith(".ntf") else ImageFormat.GEOTIFF
                    return ImageMetadata(
                        uri=file_path,
                        product_id=Path(file_path).stem,
                        sensor_id="QGIS-PYQGIS-RASTER",
                        format=fmt,
                        width=w,
                        height=h,
                        bit_depth=16,
                        band_count=bands,
                        sun_elevation_deg=45.0,
                        bbox=GeoBBox(
                            min_lon=bbox_list[0],
                            min_lat=bbox_list[1],
                            max_lon=bbox_list[2],
                            max_lat=bbox_list[3]
                        ),
                        tres={"QGIS_CRS": crs},
                        extra={"PyQgisExecuted": True, "QgisCrs": crs}
                    )
        except Exception:
            pass

        return None
