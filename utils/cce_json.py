import argparse
import json
import os

import ssg.environment

from create_srg_export import handle_rule_yaml

SSG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RULES_JSON = os.path.join(SSG_ROOT, "build", "rule_dirs.json")
BUILD_CONFIG = os.path.join(SSG_ROOT, "build", "build_config.yml")
OUTPUT = os.path.join(SSG_ROOT, 'build',
                      f'cce.json')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
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
    return parser.parse_args()

def main():
    args = parse_args()
    known_rules = list()
    with open(args.json, 'r') as f:
        known_rules = json.load(f)
    product = args.product
    product_dir = os.path.join(args.root, "products", args.product)
    product_yaml_path = os.path.join(product_dir, "product.yml")
    env_yaml = ssg.environment.open_environment(args.build_config_yaml, str(product_yaml_path))
    result = dict()

    count = 0

    for rule in known_rules.keys():

        rule_obj = handle_rule_yaml(product, known_rules[rule]['dir'], env_yaml)
        if 'cce' in rule_obj.identifiers.keys():
            cce = rule_obj.identifiers['cce']
            result[cce] = known_rules[rule]
        count += 1
        if count % 100 == 0:
            print(f"Count: {count}")

    with open(args.output, 'w') as f:
        json.dump(result, f)


if __name__ == "__main__":
    main()
