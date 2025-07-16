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

# Constants for diag_table tests
DUPLICATE_DIAG_FILE_SAME_YAML = {
    "title": "Very_Important_Title",
    "base_date": "1 1 1 0 0 0",
    "diag_files": [
        {
            "file_name": "atmos_daily",
            "freq": "1 days",
            "time_units": "time_units",
            "unlimdim": "unlimid",
            "varlist": [],
        }
    ],
}

TEST_COMBINE_TWO_SIMPLE_YAML_FILES = {
    "title": "Very_Important_Title",
    "base_date": "1 1 1 0 0 0",
    "diag_files": [
        {
            "file_name": "atmos_daily",
            "freq": "1 days",
            "time_units": "time_units",
            "unlimdim": "unlimid",
            "varlist": [
                {
                    "var_name": "tdata",
                    "module": "ocn_mod",
                    "reduction": "average",
                    "kind": "r4",
                }
            ],
        },
        {
            "file_name": "atmos_8xdaily",
            "freq": "8 hours",
            "time_units": "time_units",
            "unlimdim": "unlimid",
            "varlist": [
                {
                    "var_name": "tdata",
                    "module": "ocn_mod",
                    "reduction": "average",
                    "kind": "r4",
                }
            ],
        },
    ],
}

TEST_COMBINE_DUPLICATE_DIAG_FILES = {
    "title": "Very_Important_Title",
    "base_date": "1 1 1 0 0 0",
    "diag_files": [
        {
            "file_name": "atmos_daily",
            "freq": "1 days",
            "time_units": "time_units",
            "unlimdim": "unlimid",
            "varlist": [
                {
                    "kind": "r4",
                    "module": "ocn_mod",
                    "reduction": "average",
                    "var_name": "tdata",
                },
                {
                    "kind": "r4",
                    "module": "ocn_mod",
                    "reduction": "average",
                    "var_name": "pdata",
                },
                {
                    "kind": "r4",
                    "module": "ocn_mod",
                    "reduction": "average",
                    "var_name": "udata",
                },
            ],
        }
    ],
}
