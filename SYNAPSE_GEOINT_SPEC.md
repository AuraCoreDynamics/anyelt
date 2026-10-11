# Synapse-GEOINT Integration Specification

> **Document Identifier:** `AURA-ANYELT-SYNAPSE-001`  
> **Target Consumer:** Synapse-GEOINT Autonomous Agent Fabric  
> **Authors:** AuraCore Dynamics Engineering  

---

## 1. Overview

**Synapse-GEOINT** is an autonomous cognitive agent architecture for multi-INT and geospatial exploitation. In autonomous pipelines, agents need to interact with imagery workstations to:
1. Discover relevant imagery in catalogs.
2. Mount imagery into available workstations.
3. Pan and zoom (roam) to coordinates of interest.
4. Extract targeted chips for computer vision (YOLO, SAM, Segment Anything, ResNet).
5. Mensurate physical structures (target height from shadows, building footprints, runway lengths).
6. Perform hyperspectral classification on detected targets.

**AnyElt** serves as the authoritative interface layer between Synapse-GEOINT agents and underlying light tables.

---

## 2. Agent Tool Invocation Contracts

Synapse-GEOINT tools are parameterized via JSON schemas directly mapping to AnyElt methods:

### 2.1 Tool: `elt_search_and_load`
```json
{
  "name": "elt_search_and_load",
  "description": "Searches an imagery catalog (e.g. iSPY or GXP Xplorer) and mounts the best image into an active ELT.",
  "parameters": {
    "type": "object",
    "properties": {
      "bbox": {
        "type": "array",
        "items": { "type": "number" },
        "description": "[min_lon, min_lat, max_lon, max_lat]"
      },
      "min_niirs": { "type": "number", "default": 5.0 },
      "target_elt": { "type": "string", "enum": ["auramist", "socet_gxp", "remoteview"] }
    },
    "required": ["bbox", "target_elt"]
  }
}
```

### 2.2 Tool: `elt_mensurate_shadow`
```json
{
  "name": "elt_mensurate_shadow",
  "description": "Calculates the structural elevation of a target from its measured shadow length and sensor sun elevation.",
  "parameters": {
    "type": "object",
    "properties": {
      "elt_type": { "type": "string" },
      "shadow_length_meters": { "type": "number" },
      "sun_elevation_degrees": { "type": "number" }
    },
    "required": ["elt_type", "shadow_length_meters"]
  }
}
```

### 2.3 Tool: `elt_extract_and_classify_spectral_chip`
```json
{
  "name": "elt_extract_and_classify_spectral_chip",
  "description": "Extracts an ROI chip from a spatial ELT and passes it to Quasar for hyperspectral signature extraction and material matching.",
  "parameters": {
    "type": "object",
    "properties": {
      "source_elt": { "type": "string" },
      "roi_pixel_bounds": {
        "type": "object",
        "properties": {
          "min_x": { "type": "integer" },
          "min_y": { "type": "integer" },
          "max_x": { "type": "integer" },
          "max_y": { "type": "integer" }
        }
      },
      "candidate_material": { "type": "string" }
    },
    "required": ["source_elt", "roi_pixel_bounds", "candidate_material"]
  }
}
```

---

## 3. Reliability and Failover Policy

When a Synapse-GEOINT agent queries for an operation:
1. AnyElt queries the `EltSessionBroker`.
2. If the preferred ELT is unavailable or lacks the requested capability, AnyElt invokes `find_best_adapter` to negotiate an alternative installed tool.
3. If no adapter supports the capability, AnyElt returns an `UnsupportedCapabilityException` with alternative adapter recommendations.
