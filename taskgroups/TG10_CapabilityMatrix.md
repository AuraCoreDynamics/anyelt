# TG-010: Build-Time Capability Matrix Generator & Programmatic Reflection

> **Taskgroup Identifier:** `AURA-ANYELT-TG-010`  
> **Status:** COMPLETED  
> **Target:** `anyelt/matrix.py`, `scripts/generate_matrix.py`, `CAPABILITY_MATRIX.md`, `src/AnyElt.Adapters/EltRegistry.cs`  

## Scope & Implementation
- Implemented runtime reflection across all registered adapters to query their self-declared capabilities.
- Created `generate_capability_matrix_markdown()` producing a clean GitHub-flavored Markdown table with checkmarks (`✔` / `-`).
- Created `generate_capability_matrix_json()` outputting machine-readable JSON for agent consumption.
- Build script `scripts/generate_matrix.py` outputs `CAPABILITY_MATRIX.md` at repo root and `docs/capabilities.json`.
- Exposes matrix programmatically in Python (`anyelt.get_capability_matrix()`) and C# (`EltRegistry.GenerateCapabilityMatrixMarkdown()`).
