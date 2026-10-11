"""
AnyElt Capability Matrix Reflection & Generator.
Reflects across all self-declared ELT adapters and dynamically builds
the official capability matrix in Markdown, JSON, and Python dictionary formats.
"""

from typing import Dict, List, Any
import json

from anyelt.capabilities import EltCapability, CAPABILITY_METADATA
from anyelt.adapters import (
    AuraMistAdapter, SocetGxpAdapter, RemoteViewAdapter,
    QgisAdapter, ISpyAdapter, ImageJAdapter, QuasarAdapter
)


ALL_ADAPTER_CLASSES = [
    AuraMistAdapter,
    SocetGxpAdapter,
    RemoteViewAdapter,
    QgisAdapter,
    ISpyAdapter,
    ImageJAdapter,
    QuasarAdapter
]


def generate_capability_matrix_data() -> Dict[str, Any]:
    """
    Generate structured dictionary representation of all adapters and their capabilities.
    """
    adapters = [cls() for cls in ALL_ADAPTER_CLASSES]

    cap_list = [
        EltCapability.DIRECT_LOADING,
        EltCapability.CATALOG_SEARCH,
        EltCapability.RADIOMETRIC_ENHANCEMENT,
        EltCapability.DYNAMIC_RANGE_ADJUSTMENT,
        EltCapability.SENSOR_ROAM,
        EltCapability.GROUND_ROAM,
        EltCapability.MENSURATION_SHADOW,
        EltCapability.MENSURATION_DISTANCE,
        EltCapability.RPC_PROJECTION,
        EltCapability.CHIPPING_SENSOR,
        EltCapability.CHIPPING_GROUND,
        EltCapability.TRE_INSPECTION,
        EltCapability.MULTI_SPECTRAL,
        EltCapability.HYPERSPECTRAL,
        EltCapability.SPECTRAL_SIGNATURE,
        EltCapability.SCRIPTING_MACRO,
        EltCapability.VIEWPORT_SYNC,
        EltCapability.ORTHORECTIFICATION
    ]

    matrix_rows = []
    for a in adapters:
        row = {
            "elt_type": a.elt_type,
            "name": a.name,
            "version": a.version,
            "capabilities_mask": int(a.capabilities),
            "features": {}
        }
        for cap in cap_list:
            slug = CAPABILITY_METADATA[cap]["slug"]
            row["features"][slug] = a.has_capability(cap)
        matrix_rows.append(row)

    columns = [
        {
            "slug": CAPABILITY_METADATA[cap]["slug"],
            "name": CAPABILITY_METADATA[cap]["name"],
            "description": CAPABILITY_METADATA[cap]["description"]
        }
        for cap in cap_list
    ]

    return {
        "title": "AnyElt Universal ELT Capability Matrix",
        "total_adapters": len(adapters),
        "total_capabilities": len(cap_list),
        "columns": columns,
        "adapters": matrix_rows
    }


def generate_capability_matrix_markdown() -> str:
    """
    Generate clean, GitHub-flavored Markdown capability matrix table.
    """
    data = generate_capability_matrix_data()
    adapters = data["adapters"]
    columns = data["columns"]

    lines = [
        "# AnyElt Universal Capability Matrix",
        "",
        "> **Auto-generated at build time via runtime reflection across self-declared adapter capabilities.**",
        "> This matrix governs runtime capability negotiation, Synapse-GEOINT routing, and cross-ELT fallback selection.",
        "",
        "| ELT Platform | " + " | ".join(c["name"] for c in columns) + " |",
        "| :--- | " + " | ".join([":---:"] * len(columns)) + " |"
    ]

    for a in adapters:
        cells = [f"**{a['name']}** (`{a['elt_type']}`)"]
        for c in columns:
            has_feature = a["features"].get(c["slug"], False)
            cells.append("✔" if has_feature else "-")
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")
    lines.append("## Feature Definitions")
    lines.append("")
    for c in columns:
        lines.append(f"- **{c['name']}** (`{c['slug']}`): {c['description']}")

    return "\n".join(lines)


def generate_capability_matrix_json() -> str:
    """
    Generate JSON representation of the capability matrix.
    """
    data = generate_capability_matrix_data()
    return json.dumps(data, indent=2)
