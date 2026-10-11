#!/usr/bin/env python3
"""
Build-time script to generate AnyElt Capability Matrix files:
- CAPABILITY_MATRIX.md
- docs/capabilities.json
"""

import sys
import os
from pathlib import Path

# Add repo root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from anyelt.matrix import generate_capability_matrix_markdown, generate_capability_matrix_json


def main():
    print("Generating AnyElt Capability Matrix...")
    md_content = generate_capability_matrix_markdown()
    json_content = generate_capability_matrix_json()

    md_path = root_dir / "CAPABILITY_MATRIX.md"
    json_path = root_dir / "docs" / "capabilities.json"

    json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f" -> Wrote: {md_path}")

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_content)
    print(f" -> Wrote: {json_path}")

    print("Capability matrix generation complete.")


if __name__ == "__main__":
    main()
