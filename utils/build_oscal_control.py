import argparse
import os
import json
from pathlib import Path

import yaml

from ssg.utils import mkdir_p

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONTROL_OUT = os.path.join(SSG_ROOT, 'build', 'oscal_control.yml')
RULE_DIR_JSON = os.path.join(SSG_ROOT, 'build', 'rule_dirs.json')


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert OSCAL Catalog to Control")
    parser.add_argument("-r", "--root",
                        help=f"Root to the content project. Defaults to {SSG_ROOT}",
                        default=SSG_ROOT)
    parser.add_argument("-o", "--output", help=f"Path to output Defaults to {CONTROL_OUT}",
                        default=CONTROL_OUT)
    parser.add_argument("-j", "--json", help=f"Path to rule_dir.json. Defaults to {RULE_DIR_JSON}",
                        default=RULE_DIR_JSON)
    parser.add_argument("catalog", help="Path to OSCAL Catalog")
    return parser.parse_args()


def main():
    args = _parse_args()
    json_path = args.json
    catalog_path = args.catalog
    with open(catalog_path, 'r') as json_file:
        oscal_json = json.load(json_file)
    controls = print_group(oscal_json["catalog"]["groups"])
    output = dict()
    output["controls"] = controls
    output["title"] = oscal_json["catalog"]["metadata"]["title"]
    output["id"] = "oscal"
    output["version"] = oscal_json["catalog"]["metadata"]["version"]
    output_path = Path(args.output)
    output_dir_name = output_path.stem
    output_root = output_path.parent
    output_dir = os.path.join(output_root, output_dir_name)
    mkdir_p(output_dir)
    for control in controls:
        output = dict()
        output["controls"] = [control, ]
        filename = f'{control["id"]}.yml'
        output_filename = os.path.join(output_dir, filename)
        with open(output_filename, 'w') as f:
            f.write(yaml.dump(output, sort_keys=False))


def print_group(groups, tab="") -> list:
    groups_main = list()
    for group in groups:
        control = dict()
        control["title"] = group['title']
        control["id"] = group['id']
        control["status"] = "pending"
        control["controls"] = list()
        control["levels"] = list()
        control["levels"].append("base")
        print(f"{tab}{group['id']} - {group['title']}")
        if 'controls' in group:
            new_tab = "\t" + tab
            control["controls"].extend(print_group(group["controls"], new_tab))
        groups_main.append(control)
    return groups_main


if __name__ == "__main__":
    main()
