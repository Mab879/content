import argparse
import os
import json

import ssg.environment
import ssg.rule_yaml

from create_srg_export import handle_rule_yaml

from openpyxl import load_workbook

NO_CHANGE = 'FF92D050'
MINOR_CHANGE = 'FFFFFF00'
MAJOR_CHANGE = 'FFFFC000'
SHOW_STOPPER = 'FFFF0000'

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RULES_JSON = os.path.join(SSG_ROOT, "build", "rule_dirs.json")
CCE_JSON = os.path.join(SSG_ROOT, "build", "cce.json")
BUILD_CONFIG = os.path.join(SSG_ROOT, "build", "build_config.yml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="Path to DISA marked up")
    parser.add_argument('-s', '--sheet', help="The sheet the STIG is on, defaults to Sheet",
                        default="Sheet")
    parser.add_argument('-p', '--product',
                        help="Name of the product in the spreadsheet, defaults to RHEL 9",
                        default="RHEL 9")
    parser.add_argument("-r", "--root", type=str, action="store", default=SSG_ROOT,
                        help=f"Path to SSG root directory (defaults to {SSG_ROOT})")
    parser.add_argument("-j", "--json", type=str, action="store", default=RULES_JSON,
                        help=f"Path to the rules_dir.json (defaults to {RULES_JSON})")
    parser.add_argument("-c", "--cce", type=str, action="store", default=CCE_JSON,
                        help=f"Path to the cce.json (defaults to {CCE_JSON})")
    parser.add_argument("-b", "--build-config-yaml", default=BUILD_CONFIG,
                        help="YAML file with information about the build configuration.")
    return parser.parse_args()


def main():
    args = parse_args()
    show_stoppers = list()
    major_changes = list()
    minor_changes = list()
    no_changes = list()
    idk = list()

    workbook = load_workbook(args.file)
    sheet = workbook[args.sheet]
    cce_dict = dict()
    product = 'rhel9'
    product_dir = os.path.join(args.root, "products", product)
    product_yaml_path = os.path.join(product_dir, "product.yml")
    env_yaml = ssg.environment.open_environment(args.build_config_yaml, str(product_yaml_path))

    with open(args.cce, 'r') as f:
        cce_dict = json.load(f)

    for i in range(2, 535):
        row_fill = sheet[f'F{i}'].fill.fgColor.rgb
        srg_req = sheet[f'F{i}'].value.replace(args.product, "{{{ full_name }}}")
        cce = sheet[f'D{i}'].value
        if cce is None or cce == "":
            continue

        if row_fill == NO_CHANGE:
            continue
        elif row_fill == MINOR_CHANGE or row_fill == MAJOR_CHANGE:
            rule_obj = cce_dict[cce]
            yaml_file, yaml_contents = ssg.rule_yaml.get_yaml_contents(rule_obj)
            try:
                srg_requirement_section = ssg.rule_yaml.get_section_lines(yaml_file, yaml_contents,
                                                                      'srg_requirement')
            except ValueError:
                print(f'You figure it on {rule_obj["id"]}')
                continue
            print(rule_obj['id'])
            if srg_requirement_section is not None:

                srg_requirement_contents = ssg.rule_yaml.parse_from_yaml(yaml_contents,
                                                                         srg_requirement_section)
                srg_requirement = srg_requirement_contents['srg_requirement']

                if srg_requirement == srg_req:
                    continue

                yaml_contents = ssg.rule_yaml.update_key_value(yaml_contents, 'srg_requirement',
                                                                   f"'{srg_requirement}'", f"'{srg_req}'")
                ssg.utils.write_list_file(yaml_file, yaml_contents)
            else:
                yaml_contents = ssg.rule_yaml.add_key_value(yaml_contents, 'srg_requirement', len(yaml_contents), f"'{srg_requirement}'\n")
                ssg.utils.write_list_file(yaml_file, yaml_contents)

        else:
            continue


if __name__ == '__main__':
    main()
