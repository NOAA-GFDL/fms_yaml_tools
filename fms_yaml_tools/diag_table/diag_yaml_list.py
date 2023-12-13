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

""" Print the files and variables in a diag yaml
    Author: Tom Robinson 12/7/2023
"""

import click
import yaml
import sys

@click.command()
@click.option('--print_vars/--no-print_vars', type=click.BOOL, show_default=True, default=False,
  help="Prints the list of variables and the module they are from below each history file")
@click.option('--comma/--no-comma', type=click.BOOL, show_default=True, default=False,
  help="With --print_vars gives a comma separated list of the variables instead of a vertical listing")
@click.argument("table")
def dyl(table, print_vars, comma):
  """ Lists the history file names in a diag table YAML

      TABLE is the path of the diag table YAML file
  """
  with open(table) as fl:
    my_table = yaml.safe_load(fl)
    print_diag_file(my_table, print_vars=print_vars, comma=comma)

""" Prints the varlist for the given diag_file """
def print_diag_file_vars(my_table, diag_file, comma=False):
  if "varlist" in my_table["diag_files"][diag_file]:
    if not comma: ## The default is one variable per line
      for i in range(len(my_table["diag_files"][diag_file]["varlist"])):
        print("  -",my_table["diag_files"][diag_file]["varlist"][i]["var_name"]+" from module "+ \
             my_table["diag_files"][diag_file]["varlist"][i]["module"])
    else:
      varlist = []
      for v in my_table["diag_files"][diag_file]["varlist"]:
        varlist.append(v["var_name"])
      print(varlist)
  else:
      print(" ("+my_table['diag_files'][diag_file]["file_name"]+" has no varlist)")

""" Prints the diag_files in a diag_table.yaml """
def print_diag_file(my_table, print_vars=False, comma=False):
  for i in range(len(my_table["diag_files"])):
    print("file name:",my_table["diag_files"][i]["file_name"])
    if print_vars:
      print_diag_file_vars(my_table, i, comma)

if __name__ == '__main__':
   dyl(prog_name="dyl")
