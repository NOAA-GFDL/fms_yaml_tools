#!/usr/bin/env python3
"""
***********************************************************************
*                   GNU Lesser General Public License
*
* This file is part of the GFDL Flexible Modeling System (FMS) YAML tools.
*
* FMS_yaml_tools is free software: you can redistribute it and/or modify it under
* the terms of the GNU Lesser General Public License as published by
* the Free Software Foundation, either version 3 of the License, or (at
* your option) any later version.
*
* FMS_yaml_tools is distributed in the hope that it will be useful, but WITHOUT
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
* for more details.
*
* You should have received a copy of the GNU Lesser General Public
* License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
***********************************************************************
"""

""" Determine if a yaml data_table is valid.
    Run `python3 is_valid_data_table_yaml.py -h` for more details
    Author: Uriel Ramirez 05/27/2022
"""

import yaml
import sys
import argparse
import pkg_resources

from fms_yaml_tools.schema.validate_schema import validate_yaml

def main():
    parser = argparse.ArgumentParser(prog='is_valid_data_table_yaml', \
                                     description="Determines if a yaml data_table is valid. \
                                                  Requires pyyaml (https://pyyaml.org/) \
                                                  More details on the yaml format can be found in \
                                                  https://github.com/NOAA-GFDL/FMS/tree/main/data_override")
    parser.add_argument('-f', type=str, help='Name of the data_table yaml to check' )
    in_data_table = parser.parse_args().f

    data_path = pkg_resources.resource_filename('fms_yaml_tools', '')
    validate_yaml(in_data_table, data_path + "/schema/gfdl_msd_schemas/FMS/data_table.json", False, False)

if __name__ == "__main__":
    main()
