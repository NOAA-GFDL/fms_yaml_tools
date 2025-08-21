import click
import yaml
import logging
import copy
from .. import __version__
from collections import Counter

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('--output-yaml',  type=click.STRING, show_default=True, default="diag_table.yaml",
              help="Path to the output diag yable yaml")
@click.option('--force-write/--no-force-write', type=click.BOOL, show_default=True, default=False,
              help="Overwrite the output yaml file if it already exists")
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the conversion")
@click.version_option(__version__, "--version")
def simplify_diag_table(input_file, debug, output_yaml, force_write):
    """
    Simplify a diag_table YAML file

    Arguments:
      input_file   Path to the input diag_table YAML file.
    """

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(levelname)s: %(message)s"
    )

    logging.debug(f"Parsing the diag_table yaml: {input_file.name}")
    my_table = parse_yaml(input_file)
    simple_yaml = construct_yaml(my_table)
    dump_output_yaml(simple_yaml, output_yaml, force_write)


def parse_yaml(input_file):
    try:
        my_table = yaml.safe_load(input_file)
    except yaml.scanner.ScannerError as scanerr:
        print("ERROR:", scanerr)
        raise Exception("ERROR: Please verify that the previous entry in the yaml file is entered as "
                        "\"key: value\" and not as \"key:value\" ")

    if isinstance(my_table, str):
        raise Exception("ERROR: diagYaml contains incorrectly formatted key value pairs."
                        " Make sure that entries are formatted as \"key: value\" and not \"key:value\" ")
    return my_table


def construct_yaml(diag_yaml_file):
    diag_files = diag_yaml_file.get('diag_files', [])

    # Construct the new simple yaml:
    simple_yaml = {}
    if "title" in diag_yaml_file:
        simple_yaml['title'] = diag_yaml_file['title']
    if "base_date" in diag_yaml_file:
        simple_yaml['base_date'] = diag_yaml_file['base_date']

    simple_yaml['diag_files'] = []
    for diag_file in diag_files:
        simple_diag_file = simplify_diag_file(diag_file)
        simple_yaml['diag_files'].append(simple_diag_file)
    return simple_yaml


def dump_output_yaml(yaml_out, yaml_name, force_write):
    out_file_op = "x"  # Exclusive write
    if force_write:
        out_file_op = "w"
    myfile = open(yaml_name, out_file_op)
    yaml.dump(yaml_out, myfile, sort_keys=False)


def get_key(dictionary, key_name, error_message=""):
    if key_name not in dictionary:
        raise KeyError(f"Missing required key: {key_name} -> {error_message}")
    return dictionary.get(key_name)


def get_diag_file_info(diag_file):
    kinds = []
    reductions = []
    module_names = []
    common_keys = {}

    filename = get_key(diag_file, "file_name")
    logging.debug(f"Working on simplifying {filename}")

    if 'varlist' not in diag_file:
        logging.debug(f"The file: {filename} has no varlist, skipping ... \n")
        return

    for diag_field in diag_file['varlist']:
        varname = get_key(diag_field, 'var_name', f'filename = {filename}')
        error_message = f'filename = {filename} variable = {varname}'

        kind = get_key(diag_field, 'kind', error_message)
        kinds.append(kind)

        reduction = get_key(diag_field, 'reduction', error_message)
        reductions.append(reduction)

        module_name = get_key(diag_field, 'module', error_message)
        if module_name not in module_names:
            module_names.append(module_name)

    counts = Counter(kinds)
    common_keys['kind'] = counts.most_common(1)[0][0]

    counts = Counter(reductions)
    common_keys['reduction'] = counts.most_common(1)[0][0]

    common_keys['modules'] = module_names

    return common_keys


def remove_duplicates(diag_field, kind, reduction, module):
    if diag_field['kind'] == kind:
        diag_field.pop('kind')
    if diag_field['reduction'] == reduction:
        diag_field.pop('reduction')
    if diag_field['module'] == module:
        diag_field.pop('module')


def sort_by_module(diag_file, kind, reduction, modules):
    mod_group = []
    for module in modules:
        logging.debug(f"Getting variables from the module: {module}")

        mod = {}
        mod['module'] = module
        mod['varlist'] = []

        for diag_field in diag_file["varlist"]:
            if diag_field['module'] == module:
                mod_field = copy.deepcopy(diag_field)
                remove_duplicates(mod_field, kind, reduction, module)
                mod['varlist'].append(mod_field)

        mod_group.append(mod)
    return mod_group


def simplify_diag_file(diag_file):
    # Determine the most common kind, reduction, and unique module names
    info = get_diag_file_info(diag_file)

    # Construct the new diag_file object:
    simple_diag_file = copy.deepcopy(diag_file)

    # If nothing was returned the diag file has no variables defined so skipping
    if info is None:
        return simple_diag_file

    kind = info['kind']
    reduction = info['reduction']
    modules = info['modules']

    logging.debug(f"The most common kind is {kind}")
    logging.debug(f"The most common reduction is {reduction}")
    logging.debug(f"The modules in the file are {modules}")

    simple_diag_file['kind'] = kind
    simple_diag_file['reduction'] = reduction

    if len(modules) == 1:
        logging.debug(f"There is only 1 unique module, so not grouping the variables by module")
        simple_diag_file['module'] = modules[0]
        for diag_field in simple_diag_file['varlist']:
          remove_duplicates(diag_field, kind, reduction, modules[0])
    else:
        logging.debug(f"There are multiple unique modules, so grouping the variables by module")
        mods = sort_by_module(simple_diag_file, kind, reduction, modules)
        simple_diag_file.pop('varlist')
        simple_diag_file['modules'] = mods

    logging.debug("Finished with file! \n")
    return simple_diag_file


if __name__ == '__main__':
    simplify_diag_table()