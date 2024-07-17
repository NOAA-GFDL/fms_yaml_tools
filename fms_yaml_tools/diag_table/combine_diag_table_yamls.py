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
        verboseprint("Writing the output yaml: " + output_yaml)
        with open(output_yaml, out_file_op) as myfile:
            yaml.dump(diag_table, myfile, default_flow_style=False, sort_keys=False)

    except Exception as err:
        raise SystemExit(err)


def compare_key_value_pairs(entry1, entry2, key, is_optional=False):
    if not is_optional:
        if entry1[key] != entry2[key]:
            raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                            " with different " + key)
    else:
        if key not in entry1 and key not in entry2:
            return
        if key in entry1 and key in entry2:
            if entry1[key] != entry2[key]:
                raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                                " with different " + key)
        if key in entry1 and key not in entry2:
            raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                            " with different " + key)
        if key not in entry1 and key in entry2:
            raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                            " with different " + key)


def is_field_duplicate(diag_table, new_entry, file_name, verboseprint):
    for entry in diag_table:
        if entry == new_entry:
            verboseprint("---> " + new_entry["var_name"] + " is a duplicate variable. Moving on!")
            return True
        else:
            if entry['var_name'] != new_entry['var_name']:
                # If the variable name is not the same, then move on to the next variable
                continue
            elif entry['module'] != new_entry['module']:
                # If the variable name is the same but it a different module, then it is a brand new variable
                continue
            else:
                if entry != new_entry:
                    raise Exception("The variable " + entry['var_name'] + " from module " + entry['module'] +
                                    " in file " + file_name + " is defined twice with different keys")
    verboseprint("----> " + new_entry["var_name"] + " is a new variable. Adding it")
    return False


def is_file_duplicate(diag_table, new_entry, verboseprint):
    # Check if a diag_table entry was already defined
    for entry in diag_table:
        if entry == new_entry:
            verboseprint("---> " + new_entry["file_name"] + " is a duplicate file. Moving on!")
            return True
        else:
            # If the file_name is not the same, then move on to the next file
            if entry['file_name'] != new_entry['file_name']:
                continue

            verboseprint("---> " + entry["file_name"] + " has already been added. Checking that all "
                         + "the keys are the same")

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

            # Since the file is the same, check if there are any new variables to add to the file:
            verboseprint("---> Looking for new variables for the file " + new_entry["file_name"])
            for field_entry in new_entry['varlist']:
                if not is_field_duplicate(entry['varlist'], field_entry, entry['file_name'], verboseprint):
                    entry['varlist'].append(field_entry)
            return True
    verboseprint("---> " + new_entry["file_name"] + " is a new file. Adding it!")
    return False


def get_base_date(my_table, diag_table):
    if 'base_date' in my_table:
        diag_table['base_date'] = my_table['base_date']
    if 'title' in my_table:
        diag_table['title'] = my_table['title']


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
        verboseprint("Opening on the diag_table yaml:" + f)
        with open(f) as fl:
            verboseprint("Parsing the diag_table yaml:" + f)
            try:
                my_table = yaml.safe_load(fl)
            except yaml.YAMLError as err:
                print("---> Error when parsing the file " + f)
                raise err

        get_base_date(my_table, diag_table)

        if 'diag_files' not in my_table:
            if 'base_date' not in my_table or 'title' not in my_table:
                raise Exception("The yaml file: " + f + " does not have the " +
                                "base_date or title defined. Ensure that the first " +
                                "yaml file has the base_date and title defined!")
            continue

        diag_files = my_table['diag_files']
        for entry in diag_files:
            if not is_file_duplicate(diag_table['diag_files'], entry, verboseprint):
                diag_table['diag_files'].append(entry)
    return diag_table


if __name__ == "__main__":
    combine_diag_table_yaml(prog_name="combine_diag_table_yaml")
