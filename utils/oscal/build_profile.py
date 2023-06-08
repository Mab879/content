import argparse
import os
import pathlib
import sys

from trestle.oscal.catalog import Catalog
from trestle.oscal.profile import Import, Merge, Modify, Profile

from utils.oscal import create_metadata, get_uuid

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Given a controls file catalog create a profile")
    parser.add_argument("-o", "--output", help="Path to write the profile to", required=True)
    parser.add_argument("-c", "--catalog", help="Product to create the catalog for", required=True)
    parser.add_argument("-r", "--root", help=f"Root of the SSG project. Defaults to {SSG_ROOT}",
                        default=SSG_ROOT)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    catalog_path_str = args.catalog
    catalog_path = pathlib.Path(catalog_path_str)
    if not catalog_path.exists():
        print(f"Cannot find catalog at {str(catalog_path.absolute())}", file=sys.stderr)
        exit(3)
    catalog = Catalog.oscal_read(catalog_path)
    profile = Profile(metadata=create_metadata(f"{catalog.metadata.title} Profile"),
                      uuid=get_uuid(), imports=list())
    imp = Import(href=catalog_path_str)
    imp.include_controls = list()
    for control in catalog.controls:
        imp.include_controls.append(control.id)
    profile.imports.append(imp)
    profile.merge = Merge(as_is=True)
    profile.modify = Modify(alters=list())
    output_path = args.output
    profile.oscal_write(pathlib.Path(output_path))


if __name__ == "__main__":
    main()
