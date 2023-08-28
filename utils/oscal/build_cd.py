#! /usr/bin/python3

import argparse
import json
import os
import pathlib

from trestle.oscal.component import ComponentDefinition, DefinedComponent, ControlImplementation, \
    ImplementedRequirement

from utils.oscal import create_metadata, get_uuid
import ssg.components
import ssg.environment
import ssg.rules
import ssg.build_yaml

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RULES_JSON = os.path.join(SSG_ROOT, "build", "rule_dirs.json")
BUILD_CONFIG = os.path.join(SSG_ROOT, "build", "build_config.yml")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Given a controls file catalog create a profile")
    parser.add_argument("-o", "--output", help="Path to write the cd to", required=True)
    parser.add_argument("-r", "--root", help=f"Root of the SSG project. Defaults to {SSG_ROOT}",
                        default=SSG_ROOT)
    parser.add_argument("-p", "--product", help="Product to create the catalog for", required=True)
    parser.add_argument("-j", "--json", type=str, action="store", default=RULES_JSON,
                        help=f"Path to the rules_dir.json (defaults to {RULES_JSON})")
    parser.add_argument("-c", "--build-config-yaml", default=BUILD_CONFIG,
                        help="YAML file with information about the build configuration")
    return parser.parse_args()


def handle_rule_yaml(rule_id: str, rule_json: dict, env_yaml: dict):
    rule_dir = rule_json[rule_id]['dir']
    guide_dir = rule_json[rule_id]['guide']
    product = env_yaml['product']
    rule_obj = {'id': rule_id, 'dir': rule_dir, 'guide': guide_dir}
    rule_file = ssg.rules.get_rule_dir_yaml(rule_dir)

    rule_yaml = ssg.build_yaml.Rule.from_yaml(rule_file, env_yaml=env_yaml)
    rule_yaml.normalize(product)
    rule_obj['references'] = rule_yaml.references
    rule_obj['description'] = rule_yaml.description
    rule_obj['fixtext'] = rule_yaml.fixtext
    return rule_obj


def handle_sub_references(irs, reference, reference_name, rule_obj):
    for sub_ref in reference.split(","):
        control_id = f'{reference_name}-{sub_ref.strip()}'
        ir = create_implemented_requirement(control_id, rule_obj)
        irs.append(ir)


def create_implemented_requirement(control_id, rule_obj):
    ir = ImplementedRequirement(uuid=get_uuid(),
                                control_id
                                =control_id,
                                description=rule_obj['fixtext'])
    return ir


def setup_cd(product):
    component_definition = ComponentDefinition(metadata=create_metadata(
        f"Component definition for {product}"),
        uuid=get_uuid())
    component_definition.components = list()
    return component_definition


def create_implemented_requirements(rule_obj):
    irs = list()
    for reference_name, reference in rule_obj['references'].items():
        reference = reference.replace(' ', '_').replace('(', '_').replace(')', '')
        if ',' in reference:
            handle_sub_references(irs, reference, reference_name, rule_obj)
        else:
            control_id = f'{reference_name}-{reference}'
            ir = create_implemented_requirement(control_id, rule_obj)
            irs.append(ir)
    return irs


def get_control_implementations(env_yaml, oscal_component, rule_dir_json, ssg_component):
    oscal_component.control_implementations = list()
    product = env_yaml['product']
    for rule in ssg_component.rules:
        rule_obj = handle_rule_yaml(rule, rule_dir_json, env_yaml)
        irs = create_implemented_requirements(rule_obj)
        ci = ControlImplementation(uuid=get_uuid(), description=rule_obj['description'],
                                   source=f"{product}-catalog.json",
                                   implemented_requirements=irs)
        oscal_component.control_implementations.append(ci)


def get_rule_dir_json(json_path):
    with open(json_path, 'r') as f:
        rule_dir_json = json.load(f)
    return rule_dir_json


def get_env_yaml(build_config_yaml, product, root):
    product_dir = os.path.join(root, "products", product)
    product_yaml_path = os.path.join(product_dir, "product.yml")
    env_yaml = ssg.environment.open_environment(
        build_config_yaml, product_yaml_path,
        os.path.join(root, "product_properties"))
    return env_yaml


def main():
    args = _parse_args()
    product = args.product
    root = args.root
    json_path = args.json
    build_config_yaml = args.build_config_yaml
    components_dir = os.path.join(root, "components")
    ssg_components = ssg.components.load(components_dir)
    component_definition = setup_cd(product)
    env_yaml = get_env_yaml(build_config_yaml, product, root)
    rule_dir_json = get_rule_dir_json(json_path)

    for _, ssg_component in ssg_components.items():
        oscal_component = DefinedComponent(type="service", title=ssg_component.name,
                                           uuid=get_uuid(), description=ssg_component.name)
        get_control_implementations(env_yaml, oscal_component, rule_dir_json, ssg_component)
        component_definition.components.append(oscal_component)
    output_str = args.output
    out_path = pathlib.Path(output_str)
    component_definition.oscal_write(out_path)


if __name__ == "__main__":
    main()
