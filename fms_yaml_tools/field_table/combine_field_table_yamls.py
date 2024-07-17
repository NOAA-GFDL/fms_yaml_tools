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
@click.option('--output-yaml',  type=click.STRING, show_default=True, default="field_table.yaml",
              help="Path to the output field yable yaml")
@click.option('--force-write/--no-force-write', type=click.BOOL, show_default=True, default=False,
              help="Overwrite the output yaml file if it already exists")
@click.version_option(__version__, "--version")
def combine_field_table_yaml(in_files, debug, output_yaml, force_write):
    """ Combines a series of field_table.yaml files into one file \n
        in-files - Space seperated list with the names of the field_table.yaml files to combine \n
    """
    verboseprint = print if debug else lambda *a, **k: None
    try:
        field_table = combine_yaml(in_files, verboseprint)
        out_file_op = "x"  # Exclusive write
        if force_write:
            out_file_op = "w"
        verboseprint("Writing the output yaml: " + output_yaml)
        with open(output_yaml, out_file_op) as myfile:
            yaml.dump(field_table, myfile, default_flow_style=False)

    except Exception as err:
        raise SystemExit(err)


def field_type_exists(field_type, curr_entries):
    for entry in curr_entries:
        if field_type == entry['field_type']:
            return True
    return False


def add_new_field(new_entry, curr_entries, verboseprint):
    new_field_type = new_entry['field_type']
    for entry in curr_entries:
        if new_field_type == entry['field_type']:
            if entry == new_entry:
                # If the field_type already exists but it is exactly the same, move on
                verboseprint("---> The field_type:" + entry['field_type'] + " already exists. Moving on")
                return
            verboseprint("---> Checking for a new entry for the field_type:" + entry['field_type'])
            new_modlist = new_entry['modlist']
            for mod in new_modlist:
                if model_type_exists(mod['model_type'], entry):
                    add_new_mod(mod, entry, verboseprint)
                else:
                    # If the model type does not exist, just append it
                    verboseprint("----> Adding the model_type: " + mod['model_type'] + " to field_type:"
                                 + new_entry['field_type'])
                    entry['modlist'].append(mod)


def add_new_mod(new_mod, curr_entries, verboseprint):
    model_type = new_mod['model_type']
    for entry in curr_entries['modlist']:
        if model_type == entry['model_type']:
            if new_mod == entry:
                # If the model_type already exists but it is exactly the same, move on
                verboseprint("----> The model_type:" + entry['model_type'] + " already exists. Moving on")
                return
            verboseprint("----> Checking for a new entry for the model_type:" + entry['model_type'])
            new_varlist = new_mod['varlist']
            curr_varlist = entry['varlist']
            for new_var in new_varlist:
                found = False
                for curr_var in curr_varlist:
                    if new_var == curr_var:
                        found = True
                        verboseprint("-----> variable:" + new_var['variable'] + " already exists. Moving on")
                        break
                if not found:
                    verboseprint("-----> new variable:" + new_var['variable'] + " found. Adding it.")
                    curr_varlist.append(new_var)


def model_type_exists(model_type, curr_entries):
    for entry in curr_entries['modlist']:
        if model_type == entry['model_type']:
            return True
    return False


def combine_yaml(files, verboseprint):
    """
    Combines a list of yaml files into one

    Args:
        files: List of yaml file names to combine
    """
    field_table = {}
    field_table['field_table'] = []
    for f in files:
        verboseprint("Opening on the field_table yaml:" + f)
        # Check if the file exists
        if not path.exists(f):
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    f)
        with open(f) as fl:
            verboseprint("Parsing the data_table yaml:" + f)
            try:
                my_table = yaml.safe_load(fl)
            except yaml.YAMLError as err:
                print("---> Error when parsing the file " + f)
                raise err
            entries = my_table['field_table']
            for entry in entries:
                if not field_type_exists(entry['field_type'], field_table['field_table']):
                    verboseprint("---> Adding the field_type: " + entry['field_type'])
                    #  If the field table does not exist, just add it to the current field table
                    field_table['field_table'].append(entry)
                else:
                    add_new_field(entry, field_table['field_table'], verboseprint)
    return field_table


if __name__ == "__main__":
    combine_field_table_yaml(prog_name="combine_field_table_yaml")
