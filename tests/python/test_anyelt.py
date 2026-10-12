"""
AnyElt Comprehensive Python Test Suite.
Tests the real AuraMist and QGIS adapters, models, capabilities, cross-ELT bridging,
binary raster ingestion on disk, and matrix generators.
"""

import os
import tempfile
import pytest
import math

import anyelt
from anyelt.capabilities import EltCapability, capability_to_list, list_to_capability
from anyelt.models import (
    ImageFormat, DraMode, GeoPoint, PixelPoint, GeoBBox, PixelBBox,
    RadiometricParameters, ChipRequest, MensurationRequest, CatalogQuery
)
from anyelt.exceptions import (
    UnsupportedCapabilityException, MensurationException, BridgingException,
    ImageNotFoundException
)
from anyelt.adapters import (
    AuraMistAdapter, QgisAdapter
)
from anyelt.bridge import EltBridge, EltSessionBroker
from anyelt.matrix import generate_capability_matrix_data, generate_capability_matrix_markdown
from anyelt.io.raster import create_synthetic_nitf_bytes


def test_adapters_self_declare_capabilities():
    adapters = anyelt.get_all_adapters()
    assert len(adapters) == 2

    for a in adapters:
        assert a.name
        assert a.version == "1.0.0"
        assert a.elt_type in ("auramist", "qgis")
        assert a.capabilities != EltCapability.NONE


def test_capability_slug_conversion():
    caps = EltCapability.DIRECT_LOADING | EltCapability.MENSURATION_SHADOW
    slugs = capability_to_list(caps)
    assert "direct_loading" in slugs
    assert "mensuration_shadow" in slugs

    reconstructed = list_to_capability(slugs)
    assert reconstructed == caps


def test_auramist_adapter_full_exploitation_on_disk():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "dc_recon.ntf")
        nitf_bytes = create_synthetic_nitf_bytes("MISSION_AURAMIST_DC")
        with open(temp_file, "wb") as f:
            f.write(nitf_bytes)

        adapter = AuraMistAdapter()
        assert adapter.has_capability(EltCapability.DIRECT_LOADING)
        assert adapter.has_capability(EltCapability.MENSURATION_SHADOW)
        assert adapter.has_capability(EltCapability.RPC_PROJECTION)

        meta = adapter.load_image(temp_file)
        assert meta.product_id == "MISSION_AURAMIST_DC"
        assert meta.sun_elevation_deg == 46.8
        assert meta.rpc is not None
        assert "RPC00B" in meta.tres

        # Roam to DC coords
        vp = adapter.roam_to_geo(38.8951, -77.0364, 14.0)
        assert vp.center_geo.lat == 38.8951

        # Adjust WebGL radiometrics
        rad = adapter.apply_radiometrics(RadiometricParameters(brightness=0.3, contrast=1.5))
        assert rad.brightness == 0.3

        # Shadow Mensuration: h = L * tan(theta_sun)
        res = adapter.mensurate(MensurationRequest(
            image_uri=meta.uri,
            calculation_type="SHADOW_HEIGHT",
            shadow_length_m=20.0,
            sun_elevation_deg=46.8
        ))
        assert res.unit == "meters"
        assert 21.2 < res.calculated_value < 21.4

        # Extract real PNG chip from disk
        chip = adapter.extract_chip(ChipRequest(
            image_uri=temp_file,
            sensor_bounds=PixelBBox(0, 0, 128, 128),
            output_format="PNG"
        ))
        assert chip.width == 128
        assert chip.height == 128
        assert chip.data[0] == 0x89
        assert chip.data[1] == ord('P')
        assert chip.data[2] == ord('N')
        assert chip.data[3] == ord('G')


def test_auramist_rejects_missing_file_without_mock():
    adapter = AuraMistAdapter()
    with pytest.raises(ImageNotFoundException):
        adapter.load_image("non_existent_file.ntf")


def test_qgis_adapter_on_disk():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "sample_qgis.ntf")
        nitf_bytes = create_synthetic_nitf_bytes("QGIS_SAMPLE_01")
        with open(temp_file, "wb") as f:
            f.write(nitf_bytes)

        qgis = QgisAdapter()
        assert qgis.has_capability(EltCapability.GROUND_ROAM)
        assert not qgis.has_capability(EltCapability.SENSOR_ROAM)

        meta = qgis.load_image(temp_file)
        assert meta.product_id == "QGIS_SAMPLE_01"

        vp = qgis.roam_to_geo(38.8951, -77.0364, 12.0)
        assert vp.center_geo.lat == 38.8951

        # Sensor roam on QGIS raises UnsupportedCapabilityException
        with pytest.raises(UnsupportedCapabilityException):
            qgis.roam_to_pixel(100, 100)

        # Extract chip
        chip = qgis.extract_chip(ChipRequest(
            image_uri=temp_file,
            ground_bounds=meta.bbox,
            output_format="PNG"
        ))
        assert chip.data[0] == 0x89


def test_qgis_rejects_missing_file_without_mock():
    qgis = QgisAdapter()
    with pytest.raises(ImageNotFoundException):
        qgis.load_image("non_existent_file.tif")


def test_cross_elt_bridge_between_auramist_and_qgis():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "dc_recon.ntf")
        nitf_bytes = create_synthetic_nitf_bytes("MISSION_DC")
        with open(temp_file, "wb") as f:
            f.write(nitf_bytes)

        auramist = AuraMistAdapter()
        qgis = QgisAdapter()

        auramist.load_image(temp_file)
        qgis.load_image(temp_file)

        auramist.roam_to_geo(38.8951, -77.0364, 14.0)

        bridge = EltBridge(auramist, qgis)
        target_vp = bridge.sync_viewport()

        assert target_vp.center_geo is not None
        assert math.isclose(target_vp.center_geo.lat, 38.8951, rel_tol=1e-4)

        # Transfer chip from AuraMist to QGIS
        chip = bridge.transfer_chip(ChipRequest(
            image_uri=temp_file,
            sensor_bounds=PixelBBox(10, 10, 138, 138),
            output_format="PNG"
        ))
        assert chip.width == 128
        assert chip.height == 128
        assert chip.data[0] == 0x89


def test_session_broker_and_best_adapter():
    broker = EltSessionBroker()
    for a in anyelt.get_all_adapters():
        broker.register(a)

    best_shadow = broker.find_best_adapter(EltCapability.MENSURATION_SHADOW | EltCapability.RPC_PROJECTION)
    assert best_shadow.elt_type == "auramist"

    best_ground = broker.find_best_adapter(EltCapability.GROUND_ROAM)
    assert best_ground is not None


def test_capability_matrix_generator():
    data = generate_capability_matrix_data()
    assert data["total_adapters"] == 2
    assert data["total_capabilities"] == 18

    md = generate_capability_matrix_markdown()
    assert "# AnyElt Universal Capability Matrix" in md
    assert "✔" in md
    assert "AuraMist Web ELT Adapter" in md
    assert "QGIS PyQGIS Bridge Adapter" in md
    assert "SOCET GXP" not in md
    assert "RemoteView" not in md
    assert "iSPY" not in md


def test_api_convenience_functions_on_disk():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "dc_recon.ntf")
        nitf_bytes = create_synthetic_nitf_bytes("MISSION_DC")
        with open(temp_file, "wb") as f:
            f.write(nitf_bytes)

        adapter, meta = anyelt.open_image(temp_file, elt_type="auramist")
        assert adapter.elt_type == "auramist"
        assert meta.product_id == "MISSION_DC"

        res = anyelt.mensurate_shadow(adapter, shadow_length_m=15.0, sun_elevation_deg=45.0)
        # tan(45 deg) = 1.0 -> h = 15.0m
        assert math.isclose(res.calculated_value, 15.0, rel_tol=1e-3)
