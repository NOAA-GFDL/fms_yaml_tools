#!/usr/bin/env python3
# ***********************************************************************
# *                   GNU Lesser General Public License
# *
# * This file is part of the GFDL Flexible Modeling System (FMS) YAML tools.
# *
# * FMS_yaml_tools is free software: you can redistribute it and/or modify it under
# * the terms of the GNU Lesser General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or (at
# * your option) any later version.
# *
# * FMS_yaml_tools is distributed in the hope that it will be useful, but WITHOUT
# * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# * for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
# ***********************************************************************

""" Converts a legacy ascii diag_table to a yaml diag_table.
    Run `python3 diag_table_to_yaml.py -h` for more details
    Author: Uriel Ramirez 05/27/2022
"""

import copy as cp
import click
from os import path
import yaml
from .. import __version__


@click.command()
# Debug is used to print more information to the screen.
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the conversion")
@click.option('--output-yaml',  type=click.STRING, show_default=True, default="diag_table.yaml",
              help="Path to the output diag yable yaml")
@click.option('--force-write/--no-force-write', type=click.BOOL, show_default=True, default=False,
              help="Overwrite the output yaml file if it already exists")
@click.option('--is-segment/--full-table', type=click.BOOL, show_default=True, default=False,
              help="The diag_table is a segment and a not a full table, \
                    so the tile and the base_date are not expected")
@click.version_option(__version__, "--version")
@click.argument("diag-table-name")  # This is the path to the diag_table to convert
def diag_to_yaml(diag_table_name, debug, output_yaml, force_write, is_segment):
    """ Converts a legacy ascii diag_table to a yaml. \n
        data-table-name - data to the field table to convert \n
    """

    #: start
    test_class = DiagTable(diag_table_file=diag_table_name, is_segment=is_segment, debug=debug)
    test_class.read_and_parse_diag_table()
    test_class.construct_yaml(yaml_table_file=output_yaml,
                              force_write=force_write)


def is_duplicate(current_files, diag_file):

    """
    Determine if a diag file has already been defined.

    Args:
        current_files (list): List of dictionary containing all the diag files that have been defined
        diag_file (dictionary): Dictionary defining a diag file

    Returns:
        logical: If the diag_file has been defined and has the same keys, returns True
                 If it has been defined but it does not have the same keys, return an error
                 If it has not been defined, return False
    """
    for curr_diag_file in current_files['diag_files']:
        if curr_diag_file['file_name'] != diag_file['file_name']:
            continue
        if curr_diag_file == diag_file:
            return True
        else:
            raise Exception("The diag_table defines " + diag_file['file_name'] + " more than once with different keys")
    return False


def update_output_name(output_name, tmp_dict):
    # Ensure that the output_name contains "min"
    # if the reduction method is "min"
    if tmp_dict['reduction'] == "min" and "min" not in output_name[-3:]:
        tmp_dict['output_name'] = tmp_dict['output_name'] + "_min"

    # Ensure that the output_name contains "max"
    # if the reduction method is "max"
    if tmp_dict['reduction'] == "max" and "max" not in output_name[-3:]:
        tmp_dict['output_name'] = tmp_dict['output_name'] + "_max"

    # If the output_name and the var_name are the same
    # there is no need for output_name
    if tmp_dict['output_name'] == tmp_dict['var_name']:
        del tmp_dict['output_name']


def combine_units_and_freq(ifile_dict):
    # Combine freq_int and freq_units into 1 key
    ifile_dict['freq'] = str(ifile_dict['freq_int']) + ' ' + ifile_dict['freq_units']
    del ifile_dict['freq_int']
    del ifile_dict['freq_units']

    # Combine new_file_freq_int and new_file_freq_units into 1 key
    if "new_file_freq_int" in ifile_dict:
        ifile_dict['new_file_freq'] = str(ifile_dict['new_file_freq_int']) + ' ' + ifile_dict['new_file_freq_units']
        del ifile_dict['new_file_freq_int']
        del ifile_dict['new_file_freq_units']

    # Combine file_duration_int and file_duration_units into 1 key
    if "file_duration_int" in ifile_dict:
        ifile_dict['file_duration'] = str(ifile_dict['file_duration_int']) + ' ' + ifile_dict['file_duration_units']
        del ifile_dict['file_duration_int']
        del ifile_dict['file_duration_units']


def find_file_subregion(subregions, ifile_dict):
    found = False
    for iregion_dict in subregions:
        if iregion_dict['file_name'] != ifile_dict['file_name']:
            continue
        tmp_dict = cp.deepcopy(iregion_dict)
        del tmp_dict['file_name']
        del tmp_dict['line']
        if (tmp_dict['grid_type'] != "none"):
            ifile_dict['sub_region'].append(tmp_dict)
            found = True
            if tmp_dict['is_only_zbounds']:
                found = False
            del tmp_dict['is_only_zbounds']
            del tmp_dict['zbounds']
    if not found:
        del ifile_dict['sub_region']


def check_for_file_for_all_var(files, fields):
    """
    Determine if all fields have a file defined.

    Args:
        files (list): List of dictionary containing all the diag files that have been defined
        fields (list): List of dictionary containing all the diag fields that have been defined
    """

    for field in fields:
        found = False
        for file in files:
            if file['file_name'] == field['file_name']:
                found = True
        if not found:
            raise Exception("The variable " + field['var_name'] + " is expected to be in the file " +
                            field['file_name'] + " but the file is not defined in the diag table! " +
                            "Ensure that there is a file entry for " + field['file_name'] +
                            " or delete the the line for the field.")


def parse_region(stuff):
    parsed_region = {}
    k = -1
    for j in range(len(stuff)):
        if (stuff[j] == ""):
            continue  # Some lines have extra spaces ("1 10  9 11 -1 -1")
        k = k + 1

        # Set any -1 values to -999
        if float(stuff[j]) == -1:
            stuff[j] = "-999"

        # Define the 4 corners and the z bounds
        if k == 0:
            parsed_region['corner1'] = stuff[j]
            parsed_region['corner2'] = stuff[j]
        elif k == 1:
            parsed_region['corner3'] = stuff[j]
            parsed_region['corner4'] = stuff[j]
        elif k == 2:
            parsed_region['corner1'] = parsed_region['corner1'] + ' ' + stuff[j]
            parsed_region['corner2'] = parsed_region['corner2'] + ' ' + stuff[j]
        elif k == 3:
            parsed_region['corner3'] = parsed_region['corner3'] + ' ' + stuff[j]
            parsed_region['corner4'] = parsed_region['corner4'] + ' ' + stuff[j]
        elif k == 4:
            parsed_region['zbounds'] = stuff[j]
        elif k == 5:
            parsed_region['zbounds'] = parsed_region['zbounds'] + ' ' + stuff[j]
    return parsed_region


def set_kind(buf, iline, iline_count):
    if ("2" in buf):
        out = "r4"
    elif ("1" in buf):
        out = "r8"
    else:
        raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                        " CHECK:            " + str(iline) + '\n'
                        " Ensure that kind is either 1 or 2")
    return out


class DiagTable:
    def __init__(self, diag_table_file='Diag_Table', is_segment=False, debug=False):
        '''Initialize the diag_table type'''

        self.diag_table_file = diag_table_file
        self.is_segment = is_segment
        self.verboseprint = print if debug else lambda *a, **k: None
        self.global_section = {}
        self.global_section_keys = ['title', 'base_date']
        self.global_section_fvalues = {'title': str,
                                       'base_date': [int, int, int, int, int, int]}
        self.max_global_section = len(self.global_section_keys) - 1  # minus title

        self.file_section = []
        self.file_section_keys = ['file_name',
                                  'freq_int',
                                  'freq_units',
                                  'time_units',
                                  'unlimdim',
                                  'new_file_freq_int',
                                  'new_file_freq_units',
                                  'start_time',
                                  'file_duration_int',
                                  'file_duration_units',
                                  'filename_time_bounds']
        self.file_section_fvalues = {'file_name': str,
                                     'freq_int': int,
                                     'freq_units': str,
                                     'time_units': str,
                                     'unlimdim': str,
                                     'new_file_freq_int': int,
                                     'new_file_freq_units': str,
                                     'start_time': str,
                                     'file_duration_int': int,
                                     'file_duration_units': str,
                                     'filename_time_bounds': str}
        self.max_file_section = len(self.file_section_keys)

        self.region_section = []
        self.region_section_keys = ['grid_type',
                                    'corner1',
                                    'corner2',
                                    'corner3',
                                    'corner4',
                                    'zbounds',
                                    'is_only_zbounds',
                                    'file_name'
                                    'line']
        self.region_section_fvalues = {'grid_type': str,
                                       'corner1': [float, float],
                                       'corner2': [float, float],
                                       'corner3': [float, float],
                                       'corner4': [float, float],
                                       'zbounds': [float, float],
                                       'is_only_zbounds': bool,
                                       'file_name': str,
                                       'line': str}
        self.max_file_section = len(self.file_section_keys)
        self.field_section = []
        self.field_section_keys = ['module',
                                   'var_name',
                                   'output_name',
                                   'file_name',
                                   'reduction',
                                   'spatial_ops',
                                   'kind',
                                   'zbounds']
        self.field_section_fvalues = {'module': str,
                                      'var_name': str,
                                      'output_name': str,
                                      'file_name': str,
                                      'reduction': str,
                                      'spatial_ops': str,
                                      'kind': str,
                                      'zbounds': str}
        self.max_field_section = len(self.field_section_keys)

        self.diag_table_content = []

        #: check if diag_table file exists
        if not path.exists(self.diag_table_file):
            raise Exception('file ' + self.diag_table_file + ' does not exist')

    def read_diag_table(self):
        """ Open and read the diag_table"""
        self.verboseprint("Opening and reading the data_table:" + self.diag_table_file)
        with open(self.diag_table_file, 'r') as myfile:
            self.diag_table_content = myfile.readlines()

    def get_base_date(self, iline, iline_count):
        self.verboseprint("Getting the base_date from the line:" + iline)
        try:
            iline_list = iline.split('#')[0].split()  #: not comma separated integers
            mykey = self.global_section_keys[1]
            if len(iline_list) != 6:
                raise Exception()
            for member in iline_list:
                if int(member) < 0:
                    raise Exception()
            self.global_section[mykey] = iline.split('#')[0].strip()
            self.global_count += 1
            self.verboseprint("--->The base_date is " + self.global_section[mykey])
        except Exception:
            raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                            " CHECK:            " + str(iline) + '\n'
                            " Ensure that the second uncommented line of the diag table defines \n"
                            " the base date in the format [year month day hour min sec] \n"
                            " if this is a segment and not a full diag table use the --is-segment option. ")

    def set_title(self, iline, iline_count):
        try:
            self.verboseprint("Getting the title from the line:" + iline)
            mykey = self.global_section_keys[0]
            myfunct = self.global_section_fvalues[mykey]
            myval = myfunct(iline.strip().strip('"').strip("'"))
            self.global_section[mykey] = myval
            self.global_count += 1
            self.verboseprint("--->The title is " + self.global_section[mykey])

        except Exception:
            raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                            " CHECK:            " + str(iline) + '\n'
                            " Ensure that the first uncommented line of the diag table defines the title")

    def set_file_section(self, iline, iline_list):
        #: Fill in the file section
        tmp_dict = {}
        for i in range(len(iline_list)):
            j = i
            # Do not do anything with the "file_format" column
            if (i == 3):
                continue
            if (i > 3):
                j = i - 1
            mykey = self.file_section_keys[j]
            myfunct = self.file_section_fvalues[mykey]
            myval = myfunct(iline_list[i].strip().strip('"').strip("'"))

            # Ignore file_duration if it less than 0
            if (i == 9 and myval <= 0):
                continue

            # Ignore the file_duration_units if it is an empty string
            if (i == 10 and myval == ""):
                continue
            tmp_dict[mykey] = myval
        self.file_section.append(cp.deepcopy(tmp_dict))
        self.verboseprint("---> Parsed the file line:" + iline)
        self.verboseprint(yaml.dump(tmp_dict))

    def parse_files_and_fields(self, iline, iline_list, iline_count):
        try:
            self.set_file_section(iline, iline_list)
        except Exception:
            #: Fill in the field section
            try:
                self.set_field_section(iline, iline_list, iline_count)
            except Exception:
                raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                                " CHECK:            " + str(iline) + '\n'
                                " Ensure that the line defines a field in the format:"
                                " 'module_name', 'field_name', 'output_name', 'file_name',"
                                " 'time_sampling', 'reduction_method',"
                                " 'regional_section', 'packing' \n "
                                " Or that the line defined a file in the format: "
                                " 'file_name', 'output_freq', 'output_freq_units', 'file_format',"
                                " 'time_axis_units', 'time_axis_name'"
                                " 'new_file_freq', 'new_file_freq_units', 'start_time', 'file_duration',"
                                " 'file_duration_units'")

    def set_field_section(self, iline, iline_list, iline_count):
        tmp_dict = {}
        for i in range(len(self.field_section_keys)):
            j = i
            buf = iline_list[i]
            # Do nothing with the "time_sampling" section
            if (i == 4):
                continue
            if (i > 4):
                j = i - 1
            if (i == 5):
                # Set the reduction to average or none instead of the other options
                if "true" in buf.lower() or "avg" in buf.lower() or "mean" in buf.lower():
                    buf = "average"
                elif "false" in buf.lower():
                    buf = "none"

            # Set the kind to either "r4" or "r8"
            if (i == 7):
                buf = set_kind(buf, iline, iline_count)

            mykey = self.field_section_keys[j]
            myfunct = self.field_section_fvalues[mykey]
            myval = myfunct(buf.strip().strip('"').strip("'"))

            # Do not add the region to the field section. This will be added to the file later
            if (i != 6):
                tmp_dict[mykey] = myval
            else:
                self.set_sub_region(myval, tmp_dict)
        self.field_section.append(cp.deepcopy(tmp_dict))
        self.verboseprint("---> Parsed the field line:" + iline)
        self.verboseprint(yaml.dump(tmp_dict))

    def set_sub_region(self, myval, field_dict):
        """
        Loop through the defined sub_regions, determine if the file already has a sub_region defined
        if it does crash. If the sub_region is not already defined add the region to the list

        Args:
            myval (string): Defines the subregion as read from the diag_table in the format
                            [starting x, ending x, starting y, ending y, starting z, ending z]
            field_dict(dictionary): Defines the field
        """
        file_name = field_dict['file_name']
        found = False
        is_same = True
        for iregion_dict in self.region_section:
            if iregion_dict['file_name'] == file_name:
                found = True
                if iregion_dict['line'] != myval:
                    """
                    Here the file has a already a sub_region defined and it is not the same as the current
                    subregion.
                    """
                    is_same = False
        if (found and is_same):
            return

        tmp_dict2 = {}
        tmp_dict2["line"] = myval
        tmp_dict2["file_name"] = file_name
        self.verboseprint("Getting the subregion from " + myval)
        if "none" in myval:
            tmp_dict2[self.region_section_keys[0]] = myval
        else:
            tmp_dict2[self.region_section_keys[0]] = "latlon"
            stuff = myval.split(' ')

            parsed_region = parse_region(stuff)

            tmp_dict2["corner1"] = parsed_region['corner1']
            tmp_dict2["corner2"] = parsed_region['corner2']
            tmp_dict2["corner3"] = parsed_region['corner3']
            tmp_dict2["corner4"] = parsed_region['corner4']
            tmp_dict2["zbounds"] = parsed_region['zbounds']
            tmp_dict2["is_only_zbounds"] = False
            field_dict['zbounds'] = parsed_region['zbounds']

            if parsed_region['corner1'] == "-999 -999" and \
               parsed_region['corner2'] == "-999 -999" and \
               parsed_region['corner3'] == "-999 -999" and \
               parsed_region['corner4'] == "-999 -999":
                tmp_dict2["is_only_zbounds"] = True
            elif not is_same:
                raise Exception("The " + file_name + " has multiple sub_regions defined. Be sure that all the variables"
                                "in the file are in the same sub_region! "
                                "Region 1:" + myval + "\n"
                                "Region 2:" + iregion_dict['line'])
        self.verboseprint(yaml.dump)
        self.region_section.append(cp.deepcopy(tmp_dict2))

    def parse_diag_table(self):
        """ Loop through each line in the diag_table and parse it"""

        self.verboseprint("Parsing the data_table:" + self.diag_table_file)
        if self.diag_table_content == []:
            raise Exception('ERROR:  The input diag_table is empty!')

        iline_count, self.global_count = 0, 0

        if self.is_segment:
            self.global_count = 2

        #: The first two lines should be the title and base_time
        while self.global_count < 2:
            iline = self.diag_table_content[iline_count]
            iline_count += 1
            # Ignore comments and empty lines
            if iline.strip() != '' and '#' not in iline.strip()[0]:
                #: The second uncommented line is the base date
                if self.global_count == 1:
                    self.get_base_date(iline, iline_count)

                #: The first uncommented line is the title
                if self.global_count == 0:
                    self.set_title(iline, iline_count)

        #: The rest of the lines are either going to be file or field section
        for iline_in in self.diag_table_content[iline_count:]:
            # get rid of any leading spaces and the comma that some file lines have in the end #classic
            iline = iline_in.strip().strip(',')
            iline_count += 1
            if iline.strip() != '' and '#' not in iline.strip()[0]:  # if not blank line or comment
                iline_list = iline.split('#')[0].split(',')  # get rid of any comments in the end of a line
                self.parse_files_and_fields(iline, iline_list, iline_count)

    def get_all_files(self, in_dict):
        self.verboseprint("---> Working on file::" + in_dict['file_name'])
        ifile_dict = in_dict
        if 'ocean' in ifile_dict['file_name']:
            ifile_dict['is_ocean'] = True
        ifile_dict['sub_region'] = []

        is_static = ifile_dict['freq_int'] == -1

        combine_units_and_freq(ifile_dict)
        find_file_subregion(self.region_section, ifile_dict)

        ifile_dict['varlist'] = []
        found = False
        for ifield_dict in self.field_section:  #: field_section = [ {}, {}. {} ]
            if ifield_dict['file_name'] != ifile_dict['file_name']:
                continue
            self.verboseprint("Adding " + ifield_dict['var_name'] + " to this file")
            tmp_dict = cp.deepcopy(ifield_dict)
            if is_static and tmp_dict['reduction'] != "none":
                raise Exception("file " + ifile_dict['file_name'] +
                                " is a static file, but the variable: " + tmp_dict['output_name'] +
                                " is using " + tmp_dict['reduction'] + " as its reduction method." +
                                " The reduction method (6th column) should be none for a variables in a static file!")
            output_name = tmp_dict['output_name'].lower()
            update_output_name(output_name, tmp_dict)

            del tmp_dict['file_name']
            ifile_dict['varlist'].append(tmp_dict)
            found = True
        if not found:
            del ifile_dict['varlist']
        return ifile_dict

    def construct_yaml(self,
                       yaml_table_file='diag_table.yaml',
                       force_write=False):
        """ Combine the global, file, field, sub_region sections into 1 """

        out_file_op = "x"  # Exclusive write
        if force_write:
            out_file_op = "w"

        yaml_doc = {}
        #: title

        self.verboseprint("Constructing the yaml")
        if not self.is_segment:
            myfile = open(yaml_table_file, out_file_op)
            mykey = self.global_section_keys[0]
            yaml_doc[mykey] = self.global_section[mykey]
            yaml.dump(yaml_doc, myfile, sort_keys=False)

            yaml_doc = {}
            #: basedate
            mykey = self.global_section_keys[1]
            yaml_doc[mykey] = [int(i) for i in self.global_section[mykey].split()]
            # Hack so that the base_date is in the file as base_date = [year, month, day, hour, min, sec]
            base_date = "base_date: " + yaml.dump(yaml_doc[mykey], default_flow_style=True)
            myfile.write(base_date)

        #: diag_files
        yaml_doc = {}
        yaml_doc['diag_files'] = []
        #: go through each file
        for ifile_dict in self.file_section:  #: file_section = [ {}, {}, {} ]
            out_file_dict = self.get_all_files(ifile_dict)

            if not is_duplicate(yaml_doc, out_file_dict):
                yaml_doc['diag_files'].append(out_file_dict)
        check_for_file_for_all_var(self.file_section, self.field_section)
        self.verboseprint("Writing the output yaml: " + yaml_table_file)
        if self.is_segment:
            myfile = open(yaml_table_file, out_file_op)
        yaml.dump(yaml_doc, myfile, sort_keys=False)

    def read_and_parse_diag_table(self):
        """ Read and parse the file """
        self.read_diag_table()
        self.parse_diag_table()


if __name__ == "__main__":
    diag_to_yaml(prog_name="diag_to_yaml")
