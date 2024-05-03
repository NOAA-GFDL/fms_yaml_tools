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
import copy

@click.command()
@click.option('--fileinfo/--no-fileinfo', type=click.BOOL, show_default=True, default=False,
  help="Print all of the file information. Default only prints history file names")
@click.option('--varlist/--no-varlist', type=click.BOOL, show_default=True, default=False,
  help="Prints the list of variables and table information below each history file")
@click.option('--comma/--no-comma', type=click.BOOL, show_default=True, default=False,
  help="With --varlist gives a comma separated list of the variables instead of a vertical listing. "\
       +"Only shows variable names (no other information). "\
       +"Does nothing if --varlist isn't used.")
@click.option('--varfiles/--no-varfiles', type=click.BOOL, show_default=True, default=False,
  help="Prints variable names and a list of the files they appear in")
@click.argument("table")
def dyl(table, fileinfo, varlist, comma, varfiles):
  """ Lists the history file names in a diag table YAML

      TABLE is the path of the diag table YAML file
  """
  with open(table) as fl:
    my_table = yaml.safe_load(fl)
    print_diag_file(my_table, fileinfo, print_vars=varlist, comma=comma)
    if varfiles:
      print_varstats(my_table)
""" Prints the varlist for the given diag_file """
def print_diag_file_vars(my_table, diag_file, comma=False):
  if "varlist" in my_table["diag_files"][diag_file]:
    if not comma: ## The default is one variable per line
      for var in my_table["diag_files"][diag_file]["varlist"]:
        print(" - ",var)
    else:
      varlist = []
      for v in my_table["diag_files"][diag_file]["varlist"]:
        varlist.append(v["var_name"])
      print(" - ",varlist)
  else:
      print(" ("+my_table['diag_files'][diag_file]["file_name"]+" has no varlist)")

""" Prints information for each variable """
def print_varstats(my_table):
  nvars = 0
  allvars = []
  filenames = []
  for f in my_table["diag_files"]: #loop through files
    if "varlist" in f:
      for v in f["varlist"]:
        nvars = nvars + 1
        allvars.append(v["var_name"])
        filenames.append(f["file_name"])
#        print(v["var_name"],f["file_name"])
  for var in set(allvars):
    filelist = []
    for f in my_table["diag_files"]: #loop through files
      if "varlist" in f:
        for v in f["varlist"]:
          if v["var_name"] == var:
            filelist.append(f["file_name"])
    print (var+' in ',filelist)
#  allvarscopy = copy.deepcopy(allvars)
#  for (v,f) in zip(allvarscopy,filenames):
#    filelist = []
#    for vdup in allvars:
#      if vdup == v:
#        print (vdup,v,f)
#        filelist.append(f)
#    print(v+" in files ",filelist)



""" Prints the diag_files in a diag_table.yaml """
def print_diag_file(my_table, file_info, print_vars=False, comma=False):
  for f in my_table["diag_files"]: #loop through files
    if file_info: #Print all file info
      fonly = copy.deepcopy(f) #Create a copy and pop off the varlist
      fonly.pop("varlist", None)
      print ("FILE: ",fonly) #Print file information without the varlist
    else: #Print only the file name
      print (f["file_name"])
    if print_vars: #Print variable list/info
      i = my_table["diag_files"].index(f)
      print_diag_file_vars(my_table, i, comma)

if __name__ == '__main__':
   dyl(prog_name="dyl")
