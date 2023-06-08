import argparse
import os
import pathlib
import sys

from trestle.oscal.component import ComponentDefinition, DefinedComponent
from trestle.oscal.common import Property

from utils.oscal import create_metadata, get_uuid
import ssg.components

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Given a controls file catalog create a profile")
    parser.add_argument("-o", "--output", help="Path to write the cd to", required=True)
    parser.add_argument("-r", "--root", help=f"Root of the SSG project. Defaults to {SSG_ROOT}",
                        default=SSG_ROOT)
    parser.add_argument("-p", "--product", help="Product to create the catalog for", required=True)
    return parser.parse_args()


def main():
    args = _parse_args()
    product = args.product
    root = args.root
    components_dir = os.path.join(root, "components")
    ssg_components = ssg.components.load(components_dir)
    component_definition = ComponentDefinition(metadata=create_metadata(
        f"Component definition for {product}"),
                                               uuid=get_uuid())
    component_definition.components = list()
    for _, ssg_component in ssg_components.items():
        oscal_component = DefinedComponent(type="service", title=ssg_component.name,
                                           uuid=get_uuid(), description=ssg_component.name)

        component_definition.components.append(oscal_component)
    output_str = args.output
    out_path = pathlib.Path(output_str)
    component_definition.oscal_write(out_path)


if __name__ == "__main__":
    main()
