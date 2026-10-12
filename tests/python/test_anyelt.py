"""
AnyElt Comprehensive Python Test Suite.
Tests all 7 ELT adapters, models, capabilities, cross-ELT bridging, and matrix generators.
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
    UnsupportedCapabilityException, MensurationException, BridgingException
)
from anyelt.adapters import (
    AuraMistAdapter, SocetGxpAdapter, RemoteViewAdapter,
    QgisAdapter, ISpyAdapter, ImageJAdapter, QuasarAdapter
)
from anyelt.bridge import EltBridge, EltSessionBroker
from anyelt.matrix import generate_capability_matrix_data, generate_capability_matrix_markdown
from anyelt.io.raster import create_synthetic_nitf_bytes


def test_adapters_self_declare_capabilities():
    adapters = anyelt.get_all_adapters()
    assert len(adapters) == 7

    for a in adapters:
        assert a.name
        assert a.version == "1.0.0"
        assert a.elt_type
        assert a.capabilities != EltCapability.NONE


def test_capability_slug_conversion():
    caps = EltCapability.DIRECT_LOADING | EltCapability.MENSURATION_SHADOW
    slugs = capability_to_list(caps)
    assert "direct_loading" in slugs
    assert "mensuration_shadow" in slugs

    reconstructed = list_to_capability(slugs)
    assert reconstructed == caps


def test_auramist_adapter_full_exploitation():
    adapter = AuraMistAdapter()
    assert adapter.has_capability(EltCapability.DIRECT_LOADING)
    assert adapter.has_capability(EltCapability.MENSURATION_SHADOW)
    assert adapter.has_capability(EltCapability.RPC_PROJECTION)

    meta = adapter.load_image("nitf://auratiles/dc_recon.ntf")
    assert meta.sensor_id == "WORLDVIEW-03/PAN"
    assert meta.sun_elevation_deg == 46.8
    assert meta.rpc is not None

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


def test_socet_gxp_adapter_and_catalog():
    gxp = SocetGxpAdapter("C:/Workspaces/GEOINT")
    assert gxp.has_capability(EltCapability.CATALOG_SEARCH)
    assert gxp.has_capability(EltCapability.MULTI_SPECTRAL)

    meta = gxp.load_image("file://sandiego.ntf")
    assert meta.band_count == 4

    items = gxp.query_catalog(CatalogQuery(sensor_id="GEOEYE-01", limit=2))
    assert len(items) == 2
    assert "San Diego" in items[0].title


def test_remoteview_adapter():
    rv = RemoteViewAdapter()
    assert rv.has_capability(EltCapability.SENSOR_ROAM)
    meta = rv.load_image("C:/Imagery/rv.ntf")
    assert meta.bit_depth == 11

    # Sensor space roam
    vp = rv.roam_to_pixel(1500, 1500, 2.0)
    assert vp.center_pixel.x == 1500

    # Haversine distance
    res = rv.mensurate(MensurationRequest(
        image_uri=meta.uri,
        calculation_type="DISTANCE_2D",
        point_a_geo=GeoPoint(lat=36.85, lon=-75.97),
        point_b_geo=GeoPoint(lat=36.86, lon=-75.97)
    ))
    assert 1100 < res.calculated_value < 1120


def test_qgis_adapter_limitations():
    qgis = QgisAdapter()
    assert qgis.has_capability(EltCapability.GROUND_ROAM)
    assert not qgis.has_capability(EltCapability.SENSOR_ROAM)

    # Calling sensor roam on QGIS raises UnsupportedCapabilityException
    with pytest.raises(UnsupportedCapabilityException):
        qgis.roam_to_pixel(100, 100)


def test_ispy_catalog_only_adapter():
    ispy = ISpyAdapter()
    assert ispy.has_capability(EltCapability.CATALOG_SEARCH)
    assert not ispy.has_capability(EltCapability.DIRECT_LOADING)

    # Calling load_image on catalog-only ELT raises UnsupportedCapabilityException
    with pytest.raises(UnsupportedCapabilityException):
        ispy.load_image("local_image.ntf")

    # Catalog search works
    items = ispy.query_catalog(CatalogQuery(limit=5))
    assert len(items) > 0
    assert "Port Logistics" in items[0].title


def test_imagej_geoint_extension():
    ij = ImageJAdapter()
    assert ij.has_capability(EltCapability.RPC_PROJECTION)
    assert ij.has_capability(EltCapability.SCRIPTING_MACRO)

    meta = ij.load_image("C:/Science/chip.tif")
    assert "RPC00B" in meta.tres

    # Macro generation
    macro = ij.execute_macro(["run('Invert');", "run('Enhance Contrast', 'saturated=0.35');"])
    assert "run('Invert')" in macro
    assert "setBatchMode(true)" in macro


def test_quasar_hyperspectral_extension():
    quasar = QuasarAdapter()
    assert quasar.has_capability(EltCapability.HYPERSPECTRAL)
    assert quasar.has_capability(EltCapability.SPECTRAL_SIGNATURE)

    meta = quasar.load_image("C:/Hyperspectral/aviris.h5")
    assert meta.band_count == 224

    sig_veg = quasar.extract_spectral_signature("Pine Forest", PixelBBox(10, 10, 50, 50))
    sig_water = quasar.extract_spectral_signature("Reservoir", PixelBBox(60, 60, 100, 100))

    assert len(sig_veg.reflectance_values) == 224
    sam = quasar.compare_spectral_signatures(sig_veg, sig_water)
    assert sam > 0.1

    sam_same = quasar.compare_spectral_signatures(sig_veg, sig_veg)
    assert math.isclose(sam_same, 0.0, abs_tol=1e-5)


def test_cross_elt_bridge_viewport_sync():
    gxp = SocetGxpAdapter()
    qgis = QgisAdapter()

    gxp.load_image("file://sd.ntf")
    qgis.load_image("file://sd_map.tif")

    # Roam GXP to sensor center
    gxp.roam_to_pixel(2048, 2048, 4.0)

    # Sync to QGIS with coordinate projection
    b = EltBridge(gxp, qgis)
    target_vp = b.sync_viewport()

    assert target_vp.center_geo is not None
    assert 32.6 < target_vp.center_geo.lat < 32.8


def test_cross_elt_bridge_chip_transfer():
    gxp = SocetGxpAdapter()
    ij = ImageJAdapter()

    gxp.load_image("file://sd.ntf")

    b = EltBridge(gxp, ij)
    chip = b.transfer_chip(ChipRequest(
        image_uri="file://sd.ntf",
        sensor_bounds=PixelBBox(100, 100, 356, 356),
        output_format="PNG"
    ))

    assert chip.width == 256
    assert chip.height == 256
    assert chip.data[:4] == bytes([0x89, 0x50, 0x4E, 0x47])


def test_cross_elt_bridge_catalog_to_exploitation():
    ispy = ISpyAdapter()
    auramist = AuraMistAdapter()

    b = EltBridge(ispy, auramist)
    selected = b.search_and_load(CatalogQuery(limit=1))
    assert selected.item_id == "ISPY_RECORD_2026_0901"
    assert auramist.current_image is not None


def test_session_broker_and_best_adapter():
    broker = EltSessionBroker()
    for a in anyelt.get_all_adapters():
        broker.register(a)

    best = broker.find_best_adapter(EltCapability.HYPERSPECTRAL | EltCapability.SPECTRAL_SIGNATURE)
    assert best.elt_type == "quasar"

    best_cat = broker.find_best_adapter(EltCapability.CATALOG_SEARCH | EltCapability.MULTI_SPECTRAL)
    assert best_cat.elt_type == "socet_gxp"


def test_capability_matrix_generator():
    data = generate_capability_matrix_data()
    assert data["total_adapters"] == 7
    assert data["total_capabilities"] == 18

    md = generate_capability_matrix_markdown()
    assert "# AnyElt Universal Capability Matrix" in md
    assert "✔" in md
    assert "AuraMist Web ELT Adapter" in md


def test_api_convenience_functions():
    adapter, meta = anyelt.open_image("nitf://dc.ntf", elt_type="auramist")
    assert adapter.elt_type == "auramist"
    assert meta.sensor_id == "WORLDVIEW-03/PAN"

    res = anyelt.mensurate_shadow(adapter, shadow_length_m=15.0, sun_elevation_deg=45.0)
    # tan(45 deg) = 1.0 -> h = 15.0m
    assert math.isclose(res.calculated_value, 15.0, rel_tol=1e-3)


def test_real_nitf_binary_ingestion_and_chipping_on_disk():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "real_recon_pass.ntf")
        nitf_bytes = create_synthetic_nitf_bytes("MISSION_RECON_DC")
        with open(temp_file, "wb") as f:
            f.write(nitf_bytes)

        assert os.path.exists(temp_file)

        # Ingest via AuraMistAdapter and assert real binary decoding
        adapter = AuraMistAdapter()
        meta = adapter.load_image(temp_file)

        assert meta is not None
        assert meta.product_id == "MISSION_RECON_DC"
        assert meta.format == ImageFormat.NITF_21
        assert meta.sun_elevation_deg == 46.8
        assert "RPC00B" in meta.tres
        assert "USE00A" in meta.tres

        # Extract real PNG chip from disk
        chip = adapter.extract_chip(ChipRequest(
            image_uri=temp_file,
            sensor_bounds=PixelBBox(0, 0, 128, 128),
            output_format="PNG"
        ))

        assert chip is not None
        assert chip.width == 128
        assert chip.height == 128
        assert len(chip.data) > 50

        # Assert real PNG magic header (0x89 'P' 'N' 'G')
        assert chip.data[0] == 0x89
        assert chip.data[1] == ord('P')
        assert chip.data[2] == ord('N')
        assert chip.data[3] == ord('G')


def test_real_qgis_adapter_on_disk():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "sample_qgis.ntf")
        nitf_bytes = create_synthetic_nitf_bytes("QGIS_SAMPLE_01")
        with open(temp_file, "wb") as f:
            f.write(nitf_bytes)

        qgis = QgisAdapter()
        meta = qgis.load_image(temp_file)

        assert meta is not None
        assert meta.product_id == "QGIS_SAMPLE_01"
        assert meta.bbox is not None

        chip = qgis.extract_chip(ChipRequest(
            image_uri=temp_file,
            ground_bounds=meta.bbox,
            output_format="PNG"
        ))

        assert chip is not None
        assert chip.data[0] == 0x89
        assert chip.data[1] == ord('P')
        assert chip.data[2] == ord('N')
        assert chip.data[3] == ord('G')
