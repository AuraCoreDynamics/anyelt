"""
AnyElt Command-Line Interface (CLI).
Provides terminal commands to inspect ELTs, query capability matrices, and bridge tools.
"""

import argparse
import sys
import json

from anyelt.api import (
    get_adapter, get_all_adapters, get_capability_matrix_markdown,
    get_capability_matrix, open_image, ADAPTER_REGISTRY
)
from anyelt.capabilities import EltCapability


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="anyelt",
        description="AnyElt: Universal Electronic Light Table (ELT) Abstraction CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: matrix
    matrix_parser = subparsers.add_parser("matrix", help="Display the ELT capability matrix")
    matrix_parser.add_argument("--json", action="store_true", help="Output matrix in JSON format")

    # Command: adapters
    subparsers.add_parser("adapters", help="List all registered ELT adapters")

    # Command: inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect an image using an ELT adapter")
    inspect_parser.add_argument("uri", help="Path or URI to the image file")
    inspect_parser.add_argument("--elt", default="auramist", choices=list(ADAPTER_REGISTRY.keys()), help="Target ELT type")

    # Command: mensurate
    mens_parser = subparsers.add_parser("mensurate-shadow", help="Calculate object height from shadow length")
    mens_parser.add_argument("--length", type=float, required=True, help="Shadow length in meters")
    mens_parser.add_argument("--sun-elev", type=float, required=True, help="Sun elevation in degrees")

    args = parser.parse_args()

    if args.command == "matrix":
        if args.json:
            print(json.dumps(get_capability_matrix(), indent=2))
        else:
            print(get_capability_matrix_markdown())
    elif args.command == "adapters":
        print("Registered AnyElt Adapters:")
        for adapter in get_all_adapters():
            print(f" - {adapter.name} [{adapter.elt_type} v{adapter.version}]")
    elif args.command == "inspect":
        adapter, meta = open_image(args.uri, elt_type=args.elt)
        print(f"Loaded into {adapter.name}:")
        print(f" - Product ID: {meta.product_id}")
        print(f" - Sensor ID:  {meta.sensor_id}")
        print(f" - Format:     {meta.format.value}")
        print(f" - Dimensions: {meta.width} x {meta.height}")
        print(f" - Bit Depth:  {meta.bit_depth}")
        print(f" - Sun Elev:   {meta.sun_elevation_deg}°")
        print(f" - TRE Count:  {len(meta.tres)}")
    elif args.command == "mensurate-shadow":
        from anyelt.api import mensurate_shadow, get_adapter
        adapter = get_adapter("auramist")
        res = mensurate_shadow(adapter, args.length, args.sun_elev)
        print(f"Mensuration Result:")
        print(f" - Calculated Height: {res.calculated_value} {res.unit}")
        print(f" - Formula:           {res.formula_applied}")
        print(f" - Confidence:        {res.confidence_score * 100:.1f}%")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
