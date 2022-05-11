import os
import pathlib
import sys
from xml.etree import ElementTree as ET

import ssg.build_yaml
import ssg.controls
import ssg.environment
import ssg.rules

from utils.create_srg_export import NS, html_plain_text
from utils.disa_utils import get_severity


def get_description_root(srg: ET.Element) -> ET.Element:
    # DISA adds escaped XML to the description field
    # This method unescapes that XML and parses it
    description_xml = "<root>"
    description_xml += srg.find('xccdf-1.1:description', NS).text.replace('&lt;', '<') \
        .replace('&gt;', '>').replace(' & ', '')
    description_xml += "</root>"
    description_root = ET.ElementTree(ET.fromstring(description_xml)).getroot()
    return description_root


def get_srg_dict(xml_path: str) -> dict:
    if not pathlib.Path(xml_path).exists():
        sys.stderr.write("XML for SRG was not found\n")
        sys.stderr.write(f"Could not open file {xml_path} \n")
        exit(1)
    root = ET.parse(xml_path).getroot()
    srgs = dict()
    for group in root.findall('xccdf-1.1:Group', NS):
        for srg in group.findall('xccdf-1.1:Rule', NS):
            srg_id = srg.find('xccdf-1.1:version', NS).text
            srgs[srg_id] = dict()
            srgs[srg_id]['severity'] = get_severity(srg.get('severity'))
            srgs[srg_id]['title'] = srg.find('xccdf-1.1:title', NS).text
            description_root = get_description_root(srg)
            srgs[srg_id]['vuln_discussion'] = \
                html_plain_text(description_root.find('VulnDiscussion').text)
            srgs[srg_id]['cci'] = \
                srg.find("xccdf-1.1:ident[@system='http://cyber.mil/cci']", NS).text
            srgs[srg_id]['fix'] = srg.find('xccdf-1.1:fix', NS).text
            srgs[srg_id]['check'] = \
                html_plain_text(srg.find('xccdf-1.1:check/xccdf-1.1:check-content', NS).text)
            srgs[srg_id]['ia_controls'] = description_root.find('IAControls').text
    return srgs


def handle_rule_yaml(product: str, rule_dir: str, env_yaml: dict) -> ssg.build_yaml.Rule:
    rule_file = ssg.rules.get_rule_dir_yaml(rule_dir)

    rule_yaml = ssg.build_yaml.Rule.from_yaml(rule_file, env_yaml=env_yaml)
    rule_yaml.normalize(product)

    return rule_yaml


def get_policy(args, env_yaml) -> ssg.controls.Policy:
    policy = ssg.controls.Policy(args.control, env_yaml=env_yaml)
    policy.load()
    return policy


def get_env_yaml(root: str, product: str, build_config_yaml: str) -> dict:
    product_dir = os.path.join(root, "products", product)
    product_yaml_path = os.path.join(product_dir, "product.yml")
    env_yaml = ssg.environment.open_environment(build_config_yaml, str(product_yaml_path))
    return env_yaml
