#!/usr/bin/env python3
# ***********************************************************************
# *                   GNU Lesser General Public License
# *
# * This file is part of the GFDL Flexible Modeling System (FMS) YAML
# * tools.
# *
# * FMS_yaml_tools is free software: you can redistribute it and/or
# * modify it under the terms of the GNU Lesser General Public License
# * as published by the Free Software Foundation, either version 3 of the
# * License, or (at your option) any later version.
# *
# * FMS_yaml_tools is distributed in the hope that it will be useful, but
# * WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# * General Public License for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
# ***********************************************************************

from os import path, strerror
import errno
import click
import yaml
from .. import __version__


class InconsistentKeys(ValueError):
    """Raised when diag_file contains a varlist and a modules list."""
    def __init__(self, file_name):
        message = (
            f"The diag_file '{file_name}' defines both a top-level 'varlist' and a "
            "'modules' block. These options are mutually exclusive — please choose one."
        )
        super().__init__(message)


class DuplicateFieldError(ValueError):
    """Raised when a variable is defined twice with conflicting definitions."""
    pass


class DuplicateKeyError(ValueError):
    """Raised when a diag file is defined twice with different required keys."""
    def __init__(self, file_name, key):
        super().__init__(f"The diag_file: {file_name} is defined twice with different {key}")


class DuplicateOptionalKeyError(ValueError):
    """Raised when a diag file is defined twice with different optional keys."""
    def __init__(self, file_name, key):
        super().__init__(f"The diag_file: {file_name} is defined twice with an optional different {key}")


@click.command()
@click.argument('in-files', nargs=-1)
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the conversion")
@click.option('--output-yaml',  type=click.STRING, show_default=True, default="diag_table.yaml",
              help="Path to the output diag table yaml")
@click.option('--force-write/--no-force-write', type=click.BOOL, show_default=True, default=False,
              help="Overwrite the output yaml file if it already exists")
@click.version_option(__version__, "--version")
def combine_diag_table_yaml(in_files, debug, output_yaml, force_write):
    """ Combines a series of diag_table.yaml files into one file \n
        in-files - Space seperated list with the names of the diag_table.yaml files to combine \n
    """

    verboseprint = print if debug else lambda *a, **k: None

    try:
        diag_table = combine_yaml(in_files, verboseprint)
        out_file_op = "x"  # Exclusive write
        if force_write:
            out_file_op = "w"
        verboseprint(f"Writing the output yaml: {output_yaml}")
        with open(output_yaml, out_file_op) as myfile:
            yaml.dump(diag_table, myfile, default_flow_style=False, sort_keys=False)
    except Exception as err:
        raise SystemExit(err)


def is_outputname_different(entry, new_entry, verboseprint):
    has_outname_in = "output_name" in entry
    has_outname_new = "output_name" in new_entry

    if not has_outname_in and not has_outname_new:
        verboseprint("---> Both entries don't have output_name")
        return False

    if has_outname_in and has_outname_new:
        verboseprint("---> Both entries have output_name")
        return True

    # Exactly one entry has output_name
    if has_outname_in and not has_outname_new:
        if entry['output_name'] == entry['var_name']:
            verboseprint("---> output_name in entry equals var_name, field expected to be the same")
            return False
        else:
            verboseprint("---> Entry has output_name, new_entry does not, field not expected to be the same")
            return True

    if has_outname_new and not has_outname_in:
        if new_entry['output_name'] == new_entry['var_name']:
            verboseprint("---> output_name in new_entry equals var_name, field expected to be the same")
            return False
        else:
            verboseprint("---> New entry has output_name, entry does not, field not expected to be the same")
            return True


def compare_key_value_pairs(entry1, entry2, key, is_optional=False):
    file_name = entry1['file_name']

    if not is_optional:
        if entry1[key] != entry2[key]:
            raise DuplicateKeyError(file_name, key)
    else:
        val1 = entry1.get(key)
        val2 = entry2.get(key)

        # If key is missing in both, no issue
        if val1 is None and val2 is None:
            return

        # If one is missing or they differ, raise error
        if val1 != val2:
            raise DuplicateOptionalKeyError(file_name, key)


def is_field_duplicate(diag_table, new_entry, file_name, verboseprint):
    var_name = new_entry['var_name']
    module = new_entry.get('module')

    verboseprint(f"---> Checking if {var_name} is duplicated")

    for entry in diag_table:
        if entry == new_entry:
            verboseprint(f"---> {var_name} is a duplicate variable. Moving on!")
            return True

        # Entry is not the same as new_entry
        if entry['var_name'] != var_name:
            # If the variable name is not the same, then it is a brand new variable
            continue

        if entry.get('module') != module:
            # If the variable name is the same but it a different module, then it is a brand new variable
            continue

        # Entry and new_entry have the var_name and module, but they are not the same,
        # check if the outputname is different
        if is_outputname_different(entry, new_entry, verboseprint):
            continue

        raise DuplicateFieldError(
            f"The variable {var_name} from module {module} in file {file_name} "
            "is defined twice with different keys"
        )

    verboseprint(f"----> {var_name} is a new variable. Adding it")
    return False


def flatten_varlist(varlist):
    """Flattens a varlist that may contain nested lists."""
    flattened = []
    for item in varlist:
        if isinstance(item, list):
            flattened.extend(flatten_varlist(item))
        else:
            flattened.append(item)
    return flattened


def is_module_duplicate(diag_modules, module, file_name, verboseprint):
    module_name = module['module']
    verboseprint(f"---> Checking if {module_name} is duplicated")
    for old_module in diag_modules:
        if (old_module['module'] == module_name):
            verboseprint(f"---> Found {module_name}. Checking if it has the same keys")

            if old_module == module:
                verboseprint(f"---> {module_name} is exactly the same as the previous one. Ignoring!")
                return True
            else:
                verboseprint(f"---> {module_name} is not the same as the previous one. Checking for new variables!")
                for field_entry in module['varlist']:
                    if not is_field_duplicate(old_module['varlist'], field_entry, file_name, verboseprint):
                        old_module['varlist'].append(field_entry)
                        return True
    return False


def is_file_duplicate(diag_table, new_entry, verboseprint):
    # Check if a diag_table entry was already defined
    for entry in diag_table:
        if entry == new_entry:
            verboseprint(f"---> {new_entry['file_name']} is a duplicate file. Moving on!")
            return True
        else:
            # If the file_name is not the same, then move on to the next file
            if entry['file_name'] != new_entry['file_name']:
                continue

            verboseprint(f"---> {entry['file_name']} has already been added. Checking that all the keys are the same")

            # Since there are duplicate files, check fhat all the keys are the same:
            compare_key_value_pairs(entry, new_entry, 'freq')
            compare_key_value_pairs(entry, new_entry, 'time_units')
            compare_key_value_pairs(entry, new_entry, 'unlimdim')

            compare_key_value_pairs(entry, new_entry, 'write_file', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'new_file_freq', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'start_time', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'file_duration', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'global_meta', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'sub_region', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'is_ocean', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'reduction', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'kind', is_optional=True)

            # If entry has entry['modules'], then new_entry must also have it and it cannot have new_entry['varlist']
            # There will need be an extra layer to add the variables to entry['modules']['varlist']
            compare_key_value_pairs(entry, new_entry, 'module', is_optional=True)

            # Since the file is the same, check if there are any new variables to add to the file:
            verboseprint(f"---> Looking for new variables for the file {new_entry['file_name']}")
            if "varlist" in new_entry:
                verboseprint("This file is using a varlist do define variables")
                for field_entry in new_entry['varlist']:
                    if not is_field_duplicate(entry['varlist'], field_entry, entry['file_name'], verboseprint):
                        entry['varlist'].append(field_entry)
            elif "modules" in new_entry:
                verboseprint("This file is using modules to define variables")
                for module_entry in new_entry['modules']:
                    if not is_module_duplicate(entry['modules'], module_entry, entry['file_name'], verboseprint):
                        entry['modules'].append(module_entry)

            return True
    verboseprint(f"---> {new_entry['file_name']} is a new file. Adding it!")
    return False


def get_base_date(my_table, diag_table):
    if 'base_date' in my_table:
        diag_table['base_date'] = my_table['base_date']
    if 'title' in my_table:
        diag_table['title'] = my_table['title']


def check_inconsistent_keys(entry):
    if "modules" in entry and "varlist" in entry:
        raise InconsistentKeys(entry['file_name'])


def combine_yaml(files, verboseprint):
    diag_table = {}
    diag_table['title'] = ""
    diag_table['base_date'] = ""
    diag_table['diag_files'] = []
    for f in files:
        # Check if the file exists
        if not path.exists(f):
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    f)
        # Verify that yaml is read correctly
        try:
            verboseprint(f"Opening on the diag_table yaml: {f}")
            with open(f) as fl:
                verboseprint(f"Parsing the diag_table yaml: {f}")
                my_table = yaml.safe_load(fl)
        except yaml.scanner.ScannerError as scanerr:
            print("ERROR:", scanerr)
            raise Exception("ERROR: Please verify that the previous entry in the yaml file is entered as "
                            "\"key: value\" and not as \"key:value\" ")

        if isinstance(my_table, str):
            raise Exception("ERROR: diagYaml contains incorrectly formatted key value pairs."
                            " Make sure that entries are formatted as \"key: value\" and not \"key:value\" ")

        verboseprint("Attempting to get the base_date")
        get_base_date(my_table, diag_table)

        diag_files = my_table['diag_files']
        for entry in diag_files:
            check_inconsistent_keys(entry)
            if 'varlist' in entry:
                entry['varlist'] = flatten_varlist(entry['varlist'])
            if not is_file_duplicate(diag_table['diag_files'], entry, verboseprint):
                diag_table['diag_files'].append(entry)

    if diag_table['base_date'] == "" or diag_table['title'] == "":
        raise ValueError("The ouput combined yaml file does not have the base_date or title defined. "
                         "Ensure that one yaml file has the base_date and title defined!")
    return diag_table


if __name__ == "__main__":
    combine_diag_table_yaml(prog_name="combine_diag_table_yaml")
