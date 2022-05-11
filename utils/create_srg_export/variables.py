import pathlib
import re
import sys

import yaml

from utils.create_srg_export import html_plain_text


def get_variable_value(root_path: str, product: str, name: str, selector: str) -> str:
    product_value_full_path = pathlib.Path(root_path).joinpath('build').joinpath(product)\
        .joinpath('values').joinpath(f'{name}.yml').absolute()
    if not product_value_full_path.exists():
        sys.stderr.write(f'Undefined variable {name}\n')
        exit(7)
    with open(product_value_full_path, 'r') as f:
        var_yaml = yaml.load(Loader=yaml.BaseLoader, stream=f)
        if 'options' not in var_yaml:
            sys.stderr.write(f'No options for {name}\n')
            exit(8)
        if not selector and 'default' not in var_yaml['options']:
            sys.stderr.write(f'No default selector for {name}\n')
            exit(10)
        if not selector:
            return str(var_yaml['options']['default'])

        if selector not in var_yaml['options']:
            sys.stderr.write(f'Option {selector} does not exist for {name}\n')
            exit(9)
        else:
            return str(var_yaml['options'][selector])


def replace_variables(source: str, variables: dict, root_path: str, product: str) -> str:
    result = source
    if source:
        sub_element_regex = r'<sub idref="([a-z0-9_]+)" \/>'
        matches = re.finditer(sub_element_regex, source, re.MULTILINE)
        for match in matches:
            name = match.group(1)
            value = get_variable_value(
                root_path, product, name, variables.get(name))
            result = result.replace(match.group(), value)
    return result


def handle_variables(source: str, variables: dict, root_path: str, product: str) -> str:
    result = replace_variables(source, variables, root_path, product)
    return html_plain_text(result)
