#!/usr/bin/env python3

import argparse
import csv
import datetime
import os

import yaml

from utils.build_stig_control import get_implemented_stigs


SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUILD_CONFIG = os.path.join(SSG_ROOT, "build", "build_config.yml")
OUTPUT = os.path.join(SSG_ROOT, 'build',
                      f'{datetime.datetime.now().strftime("%s")}_stig_import.yml')
RULES_JSON = os.path.join(SSG_ROOT, "build", "rule_dirs.json")

SEVERITY = {'CAT III': 'low', 'CAT II': 'medium', 'CAT I': 'high'}
STATUS = {'Applicable - Inherently Meets': 'inherently met', "Not Applicable": "not applicable",
          'Applicable - Configurable': 'automated', 'Applicable - Does Not Meet': 'does not met'}


def parse_args():
    # Heavily copied from utils/build_stig_control.py
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str, help="Name of existing STIG CSV file to import")
    parser.add_argument("-j", "--json", type=str, action="store", default=RULES_JSON,
                        help=f"Path to the rules_dir.json (defaults to {RULES_JSON})")
    parser.add_argument("-p", "--product", type=str, action="store", required=True,
                        help="What product to get SRGs for")
    parser.add_argument("-ref", "--reference", type=str, default="srg",
                        help="Reference system to check for, defaults to srg")
    parser.add_argument("-r", "--root", type=str, action="store", default=SSG_ROOT,
                        help="Path to SSG root directory (defaults to %s)" % SSG_ROOT)
    parser.add_argument("-c", "--build-config-yaml", default=BUILD_CONFIG,
                        help="YAML file with information about the build configuration")
    return parser.parse_args()


def main():
    args = parse_args()
    controls = list()
    implement_rules = get_implemented_stigs(args)
    with open(args.source) as f:
        reader = csv.DictReader(f)
        for row in reader:
            srg = row['SRGID']
            control = dict()
            control['id'] = srg
            control['description'] = row['SRG Requirement']
            control['rationale'] = row['VulDiscussion']
            control['severity'] = [SEVERITY[row['Severity']], ]
            control['status'] = STATUS[row['Status'].strip()]
            # These might help, not sure how to format them better
            control['notes'] = f"check - {row['Check']}\n\n fix {row['Fix']}"
            if srg in implement_rules.keys():
                control['rules'] = implement_rules.get(srg)
            controls.append(control)
    with open(OUTPUT, 'w') as f:
        yaml.dump(controls, f, sort_keys=False)
    print(OUTPUT)


if __name__ == '__main__':
    main()
