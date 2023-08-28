#! /usr/bin/python3

import argparse
import os
import pathlib
import sys

from trestle.oscal.catalog import Catalog, Control

import ssg.products
from ssg.controls import ControlsManager
from utils.oscal import create_metadata, get_uuid

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Path to write the catalog to")
    parser.add_argument("-p", "--product", help="Product to create the catalog for", required=True)
    parser.add_argument("-c", "--control", help="Control to create catalog for", required=True)
    parser.add_argument("-r", "--root", help=f"Root of the SSG project. Defaults to {SSG_ROOT}",
                        default=SSG_ROOT)
    parser.add_argument("--cis", help="Assume that given control is for a CIS profile",
                        action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    product = args.product
    product_filename = os.path.join(SSG_ROOT, "products", product, "product.yml")
    product_env = ssg.products.load_product_yaml(product_filename)
    root_path = args.root
    controls_dir = os.path.join(root_path, "controls")
    controls_manager = ControlsManager(controls_dir=controls_dir, env_yaml=product_env)
    controls_manager.load()
    policy = args.control
    if policy not in controls_manager.policies:
        print(f"Unable to find policy {policy}", file=sys.stderr)
        exit(2)
    metadata = create_metadata(f"{product} {policy} Catalog")
    catalog = Catalog(metadata=metadata, uuid=get_uuid())
    catalog.controls = list()
    policy_controls = controls_manager.get_all_controls(policy)
    for policy_control in policy_controls:
        oscal_id = policy_control.id
        if args.cis:
            oscal_id = f"CIS-{oscal_id}"
        oscal_control = Control(id=oscal_id, title=policy_control.title)
        catalog.controls.append(oscal_control)
    out_path = pathlib.Path(args.output)
    catalog.oscal_write(out_path)
    print(f"Wrote catalog {str(out_path.absolute())}")


if __name__ == "__main__":
    main()
