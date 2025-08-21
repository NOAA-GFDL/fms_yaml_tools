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

# This file contains classes shared among the different tests

class DiagField:
    def __init__(self, var_name, module, reduction, kind, output_name=None):
        self.var_name = var_name
        self.module = module
        self.reduction = reduction
        self.kind = kind
        self.output_name = output_name

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class DiagFile:
    def __init__(self, file_name, freq, time_units, unlimdim,
                 start_time=None, module=None, reduction=None, kind=None):
        self.varlist = []

        self.file_name = file_name
        self.freq = freq
        self.time_units = time_units
        self.unlimdim = unlimdim
        self.start_time = start_time
        self.module = module
        self.reduction = reduction
        self.kind = kind

    def append_to_varlist(self, vars):
        self.varlist.extend(vars)

    def to_dict(self):
        data = {
            k: v for k, v in self.__dict__.items() if v is not None and k != "varlist"
        }
        data["varlist"] = [var.to_dict() for var in self.varlist]
        return data


class DiagYamlFile:
    def __init__(self):
        self.diag_files = []

    def set_title_basedate(self):
        self.title = "Very_Important_Title"
        self.base_date = "1 1 1 0 0 0"

    def append_to_diag_files(self, diag_files):
        for diag_file in diag_files:
            self.diag_files.append(diag_file)

    def to_dict(self):
        # Return a plain dict with all the relevant data, recursively converting nested objects if needed
        out = {}
        if hasattr(self, "title") and self.title:
            out["title"] = self.title
        if hasattr(self, "base_date") and self.base_date:
            out["base_date"] = self.base_date

        out["diag_files"] = [df.to_dict() for df in self.diag_files]
        return out
