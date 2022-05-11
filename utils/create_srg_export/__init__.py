#!/usr/bin/python3

import argparse
import csv
import datetime
import json
import pathlib
import os
import re
import sys
import string

from typing.io import TextIO

from utils.create_srg_export.data import get_srg_dict, handle_rule_yaml, get_policy, get_env_yaml
from utils.create_srg_export.output import handle_output
from utils.create_srg_export.variables import handle_variables
from utils.disa_utils import get_iacontrol, get_severity, DisaStatus

try:
    import ssg.build_yaml
    import ssg.constants
    import ssg.controls
    import ssg.environment
    import ssg.rules
    import ssg.yaml
except (ModuleNotFoundError, ImportError):
    sys.stderr.write("Unable to load ssg python modules.\n")
    sys.stderr.write("Hint: run source ./.pyenv.sh\n")
    exit(3)

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RULES_JSON = os.path.join(SSG_ROOT, "build", "rule_dirs.json")
BUILD_CONFIG = os.path.join(SSG_ROOT, "build", "build_config.yml")
OUTPUT = os.path.join(SSG_ROOT, 'build',
                      f'{datetime.datetime.now().strftime("%s")}_stig_export.csv')
SRG_PATH = os.path.join(SSG_ROOT, 'shared', 'references', 'disa-os-srg-v2r2.xml')
NS = {'scap': ssg.constants.datastream_namespace,
      'xccdf-1.2': ssg.constants.XCCDF12_NS,
      'xccdf-1.1': ssg.constants.XCCDF11_NS}
SEVERITY = {'low': 'CAT III', 'medium': 'CAT II', 'high': 'CAT I'}

HEADERS = [
    'IA Control', 'CCI', 'SRGID', 'STIGID', 'SRG Requirement', 'Requirement',
    'SRG VulDiscussion', 'Vul Discussion', 'Status', 'SRG Check', 'Check', 'SRG Fix',
    'Fix', 'Severity', 'Mitigation', 'Artifact Description', 'Status Justification'
    ]

COLUMNS = string.ascii_uppercase[:17]  # A-Q uppercase letters

COLUMN_MAPPINGS = dict(zip(COLUMNS, HEADERS))


def html_plain_text(source: str) -> str:
    if source is None:
        return ""
    # Quick and dirty way to clean up HTML fields.
    # Add line breaks
    result = source.replace("<br />", "\n")
    result = result.replace("<br/>", "\n")
    result = result.replace("<tt>", '"')
    result = result.replace("</tt>", '"')
    # Remove all other tags
    result = re.sub(r"(?s)<.*?>", " ", result)

    # only replace this after replacing other tags as < and >
    # would be caught by the generic substitution
    result = result.replace("&gt;", ">")
    result = result.replace("&lt;", "<")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--control', type=str, action="store", required=True,
                        help="The control file to parse")
    parser.add_argument('-o', '--output', type=str,
                        help=f"The path to the output. Defaults to {OUTPUT}",
                        default=OUTPUT)
    parser.add_argument("-r", "--root", type=str, action="store", default=SSG_ROOT,
                        help=f"Path to SSG root directory (defaults to {SSG_ROOT})")
    parser.add_argument("-j", "--json", type=str, action="store", default=RULES_JSON,
                        help=f"Path to the rules_dir.json (defaults to {RULES_JSON})")
    parser.add_argument("-p", "--product", type=str, action="store", required=True,
                        help="What product to get STIGs for")
    parser.add_argument("-b", "--build-config-yaml", default=BUILD_CONFIG,
                        help="YAML file with information about the build configuration.")
    parser.add_argument("-m", "--manual", type=str, action="store",
                        help="Path to XML XCCDF manual file to use as the source of the SRGs",
                        default=SRG_PATH)
    parser.add_argument("-f", "--out-format", type=str, choices=("csv", "xlsx", "html"),
                        action="store", help="The format the output should take. Defaults to csv",
                        default="csv")
    return parser.parse_args()


def get_requirement(control: ssg.controls.Control, rule_obj: ssg.build_yaml.Rule) -> str:
    if rule_obj.srg_requirement != "":
        return rule_obj.srg_requirement
    else:
        return control.title()


def set_status(control, row):
    if control.status is not None:
        row['Status'] = DisaStatus.from_string(control.status)
    else:
        row['Status'] = DisaStatus.AUTOMATED


def get_check(control, product, root_path, rule_object):
    ocil_var = handle_variables(rule_object.ocil, control.variables, root_path,
                                product)
    ocil_clause_var = handle_variables(rule_object.ocil_clause, control.variables,
                                       root_path, product)
    check = f'{ocil_var}\n\n' \
            f'If {ocil_clause_var}, then this is a finding.'
    return check


def handle_control(product: str, control: ssg.controls.Control, env_yaml: ssg.environment,
                   rule_json: dict, srgs: dict, used_rules: list, root_path: str) -> list:

    if len(control.selections) > 0:
        rows = list()
        for selection in control.selections:
            if selection not in used_rules and selection in control.selected:
                rule_object = handle_rule_yaml(product, rule_json[selection]['dir'], env_yaml)
                row = create_base_row(control, srgs, rule_object)
                if control.levels is not None:
                    row['Severity'] = get_severity(control.levels[0])
                row['Requirement'] = get_requirement(control.title, rule_object)
                row['Vul Discussion'] = handle_variables(rule_object.rationale, control.variables,
                                                         root_path, product)
                row['Check'] = get_check(control, product, root_path, rule_object)
                row['Fix'] = handle_variables(rule_object.fixtext, control.variables, root_path,
                                              product)
                row['STIGID'] = rule_object.identifiers.get('cce', "")
                set_status(control, row)
                used_rules.append(selection)
                rows.append(row)
        return rows
    else:
        return [no_selections_row(control, srgs)]


def no_selections_row(control, srgs):
    row = create_base_row(control, srgs, ssg.build_yaml.Rule('null'))
    row['Requirement'] = control.title
    row['Status'] = DisaStatus.from_string(control.status)
    row['Fix'] = control.fixtext
    row['Check'] = control.check
    row['Vul Discussion'] = html_plain_text(control.rationale)
    row["STIGID"] = ""
    return row


def create_base_row(item: ssg.controls.Control, srgs: dict,
                    rule_object: ssg.build_yaml.Rule) -> dict:
    row = dict()
    srg_id = item.id
    if srg_id not in srgs:
        print(f"Unable to find SRG {srg_id}. Id in the control must be a valid SRGID.")
        exit(4)
    srg = srgs[srg_id]

    row['SRGID'] = rule_object.references.get('srg', srg_id)
    row['CCI'] = rule_object.references.get('disa', srg['cci'])
    row['SRG Requirement'] = srg['title']
    row['SRG VulDiscussion'] = srg['vuln_discussion']
    row['SRG Check'] = srg['check']
    row['SRG Fix'] = srg['fix']
    row['Severity'] = get_severity(srg.get('severity'))
    row['IA Control'] = get_iacontrol(row['SRGID'])
    row['Mitigation'] = item.mitigation
    row['Artifact Description'] = item.artifact_description
    row['Status Justification'] = item.status_justification
    return row


def setup_csv_writer(csv_file: TextIO) -> csv.DictWriter:
    csv_writer = csv.DictWriter(csv_file, HEADERS)
    csv_writer.writeheader()
    return csv_writer


def get_rule_json(json_path: str) -> dict:
    with open(json_path, 'r') as json_file:
        rule_json = json.load(json_file)
    return rule_json


def check_paths(control_path: str, rule_json_path: str) -> None:
    control_full_path = pathlib.Path(control_path).absolute()
    if not control_full_path.exists():
        sys.stderr.write(f"Unable to find control file {control_full_path}\n")
        exit(5)
    rule_json_full_path = pathlib.Path(rule_json_path).absolute()
    if not rule_json_full_path.exists():
        sys.stderr.write(f"Unable to find rule_dirs.json file {rule_json_full_path}\n")
        sys.stderr.write("Hint: run ./utils/rule_dir_json.py\n")
        exit(2)


def check_product_value_path(root_path: str, product: str) -> None:
    product_value_full_path = pathlib.Path(root_path).joinpath('build')\
        .joinpath(product).joinpath('values').absolute()
    if not pathlib.Path.exists(product_value_full_path):
        sys.stderr.write(f"Unable to find values directory for"
                         f" {product} in {product_value_full_path}\n")
        sys.stderr.write(f"Have you built {product}\n")
        exit(6)


def main() -> None:
    args = parse_args()
    check_paths(args.control, args.json)
    check_product_value_path(args.root, args.product)

    srgs = get_srg_dict(args.manual)
    env_yaml = get_env_yaml(args.root, args.product, args.build_config_yaml)
    policy = get_policy(args, env_yaml)
    rule_json = get_rule_json(args.json)

    used_rules = list()
    results = list()
    for control in policy.controls:
        rows = handle_control(args.product, control, env_yaml, rule_json, srgs, used_rules,
                              args.root)
        results.extend(rows)

    handle_output(args.output, results, args.out_format, args.product)


if __name__ == '__main__':
    main()
