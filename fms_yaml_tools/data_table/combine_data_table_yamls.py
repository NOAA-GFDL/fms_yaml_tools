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
@click.option('--output-yaml',  type=click.STRING, show_default=True, default="data_table.yaml",
              help="Path to the output data table yaml")
@click.option('--force-write/--no-force-write', type=click.BOOL, show_default=True, default=False,
              help="Overwrite the output yaml file if it already exists")
@click.version_option(__version__, "--version")
def combine_data_table_yaml(in_files, debug, output_yaml, force_write):
    """ Combines a series of data_table.yaml files into one file \n
        in-files - Space seperated list with the names of the data_table.yaml files to combine \n
    """

    verboseprint = print if debug else lambda *a, **k: None
    try:
        data_table = combine_yaml(in_files, verboseprint)
        out_file_op = "x"  # Exclusive write
        if force_write:
            out_file_op = "w"
        verboseprint("Writing the output yaml: " + output_yaml)
        with open(output_yaml, out_file_op) as myfile:
            yaml.dump(data_table, myfile, default_flow_style=False)

    except Exception as err:
        raise SystemExit(err)


def is_duplicate(data_table, new_entry):
    """
    Check if a data_table entry was already defined in a different file

    Args:
        data_table: List of dictionaries containing all of the data_table
                    entries that have been combined
        new_entry: Dictionary of the data_table entry to check
    """

    for entry in data_table:
        if entry == new_entry:
            is_duplicate = True
            return is_duplicate
        else:
            if entry['fieldname_in_model'] == new_entry['fieldname_in_model']:
                raise Exception("A data_table entry is defined twice for the "
                                "fieldname_in_model:" + entry['fieldname_in_model'] +
                                " with different keys/values!")
    is_duplicate = False
    return is_duplicate


def combine_yaml(files, verboseprint):
    """
    Combines a list of yaml files into one

    Args:
        files: List of yaml file names to combine
    """
    data_table = {}
    data_table['data_table'] = []
    for f in files:
        # Check if the file exists
        verboseprint("Opening on the data_table yaml:" + f)
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
            entries = my_table['data_table']
            for entry in entries:
                verboseprint("---> Working on the entry: \n" + yaml.dump(entry))
                verboseprint("Checking if it is a duplicate:")
                if not is_duplicate(data_table['data_table'], entry):
                    verboseprint("It is not a duplicate so adding it")
                    data_table['data_table'].append(entry)
    return data_table


if __name__ == "__main__":
    combine_data_table_yaml(prog_name="combine_data_table_yaml")
