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
import yaml
import click
from .. import __version__, TableParseError


@click.command()
# Debug is used to print more information to the screen.
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the conversion")
@click.option('--output-yaml',  type=click.STRING, show_default=True, default="data_table.yaml",
              help="Path to the output data yable yaml")
@click.option('--force-write/--no-force-write', type=click.BOOL, show_default=True, default=False,
              help="Overwrite the output yaml file if it already exists")
@click.version_option(__version__, "--version")
@click.argument("data-table-name")  # This is the path to the data_table to convert
def data_to_yaml(data_table_name, debug, output_yaml, force_write):
    """ Converts a legacy ascii data_table to a yaml. \n
        data-table-name - data to the field table to convert \n
    """
    try:
        test_class = DataType(data_table_file=data_table_name,
                              yaml_table_file=output_yaml,
                              force_write=force_write, debug=debug)
        test_class.convert_data_table()
    except Exception as err:
        raise SystemExit(err)


class DataType:
    def __init__(self, data_table_file='data_table',
                 yaml_table_file='data_table.yaml',
                 force_write=False, debug=False):
        """Initialize the DataType"""
        self.data_table_file = data_table_file
        self.yaml_table_file = yaml_table_file
        self.verboseprint = print if debug else lambda *a, **k: None
        self.out_file_op = "x"  # Exclusive write
        if force_write:
            self.out_file_op = "w"

        self.data_type = {}
        self.data_type_keys = ['grid_name',
                               'fieldname_in_model',
                               'fieldname_in_file',
                               'file_name',
                               'interp_method',
                               'factor',
                               'lon_start',
                               'lon_end',
                               'lat_start',
                               'lat_end',
                               'type']
        self.data_type_values = {'grid_name': str,
                                 'fieldname_in_model': str,
                                 'fieldname_in_file': str,
                                 'file_name': str,
                                 'interp_method': str,
                                 'factor': float,
                                 'lon_start': float,
                                 'lon_end': float,
                                 'lat_start': float,
                                 'lat_end': float,
                                 'type': str}

        self.data_table_content = []

        #: check if data_table file exists
        if not path.exists(self.data_table_file):
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    data_table_file)

        # Check if path to the output yaml file exists
        if not path.exists(path.abspath(path.dirname(self.yaml_table_file))):
            raise NotADirectoryError(errno.ENOTDIR,
                                     "Directory does not exist",
                                     path.abspath(
                                        path.dirname(self.yaml_table_file)))

    def read_data_table(self):
        """Open and read the legacy ascii data_table file"""
        with open(self.data_table_file, 'r') as myfile:
            self.data_table_content = myfile.readlines()

    def parse_data_table(self):
        """Loop through each line in the ascii data_Table file and fill in
           data_type class"""
        iline_count = 0
        self.data_type['data_table'] = []
        for iline in self.data_table_content:
            iline_count += 1
            if iline.strip() != '' and '#' not in iline.strip()[0]:
                self.verboseprint("---> Working on line:" + iline.replace("\n", ""))
                # get rid of comment at the end of line
                iline_list = iline.split('#')[0].split(',')
                try:
                    tmp_list = {}
                    for i in range(len(iline_list)):
                        mykey = self.data_type_keys[i]
                        myfunct = self.data_type_values[mykey]
                        myval = myfunct(
                            iline_list[i].strip('"\' \n'))
                        if i == 4:
                            # If LIMA format convert to the regular format
                            # #FUTURE
                            if ("true" in myval):
                                myval = 'bilinear'
                            if ("false" in myval):
                                myval = 'none'
                            if ("default" in myval):
                                myval = 'bilinear'
                        tmp_list[mykey] = myval
                except Exception:
                    raise TableParseError(self.data_table_file,
                                          iline_count,
                                          iline)
                data_table_entry = reformat_yaml(tmp_list)
                self.verboseprint("Yaml for this line:")
                self.verboseprint(yaml.dump(data_table_entry, sort_keys=False))
                self.data_type['data_table'].append(data_table_entry)

    def read_and_parse_data_table(self):
        """Open, read, and parse the legacy ascii data_table file"""
        if self.data_table_content != []:
            self.data_table_content = []

        self.verboseprint("Opening and reading the data_table:" + self.data_table_file)
        self.read_data_table()

        self.verboseprint("Parsing the data_table:" + self.data_table_file)
        self.parse_data_table()

    def convert_data_table(self):
        """Convert the legacy ascii data_table file to yaml"""
        self.read_and_parse_data_table()

        self.verboseprint("Writing the output yaml: " + self.yaml_table_file)
        with open(self.yaml_table_file, self.out_file_op) as myfile:
            yaml.dump(self.data_type, myfile, sort_keys=False)


def reformat_yaml(tmp_list):
    """Convert the dictionary as it was read in to the output yaml"""
    data_table_entry = {}
    data_table_entry['grid_name'] = tmp_list['grid_name']
    data_table_entry['fieldname_in_model'] = tmp_list['fieldname_in_model']
    data_table_entry['factor'] = tmp_list['factor']
    if tmp_list['fieldname_in_file'] != "":
        override_file = {}
        override_file['file_name'] = tmp_list['file_name']
        override_file['fieldname_in_file'] = tmp_list['fieldname_in_file']
        override_file['interp_method'] = tmp_list['interp_method']
        if ":" in tmp_list['file_name']:
            multi_file = {}
            file_name_str = tmp_list['file_name']
            if file_name_str.count(':') != 2:
                raise Exception("If using the multi-file capability. Three filename must be set, seperated by a comma.")

            file_names = file_name_str.split(":")
            multi_file['prev_file_name'] = file_names[0]
            multi_file['next_file_name'] = file_names[2]
            override_file['file_name'] = file_names[1]
            override_file['multi_file'] = []
            override_file['multi_file'].append(multi_file)
        else:
            override_file['file_name'] = tmp_list['file_name']

        if 'type' in tmp_list:
            subregion = {}
            subregion['lon_start'] = tmp_list['lon_start']
            subregion['lon_end'] = tmp_list['lon_end']
            subregion['lat_start'] = tmp_list['lat_start']
            subregion['lat_end'] = tmp_list['lat_end']
            subregion['type'] = tmp_list['type']
            data_table_entry['subregion'] = []
            data_table_entry['subregion'].append(subregion)
        data_table_entry['override_file'] = []
        data_table_entry['override_file'].append(override_file)

    return data_table_entry


if __name__ == "__main__":
    data_to_yaml(prog_name="data_to_yaml")
