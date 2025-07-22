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

TEST_DIAG_ANCHORS = {
    'title': 'test_none',
    'base_date': '2 1 1 0 0 0',
    'diag_files': [
        {
            'file_name': 'atmos_daily',
            'freq': '1 days',
            'time_units': 'hours',
            'unlimdim': 'time',
            'module': 'ocn_mod',
            'reduction': 'none',
            'kind': 'r4',
            'varlist': [
                {'var_name': 'var0'},
                {'var_name': 'var1'},
                {'var_name': 'var2'},
                {'var_name': 'var3'},
                {'var_name': 'var4'},
                {
                    'var_name': 'var3',
                    'output_name': 'var3_Z',
                    'zbounds': '2. 3.'
                },
                {'var_name': 'var773'},
                {'var_name': 'var609'}
            ]
        }
    ]
}

DIAG_TABLE_YAML_ANCHORS = """\
common_vars: &common_vars
  - var_name: var0
  - var_name: var1
  - var_name: var2
  - var_name: var3
  - var_name: var4
  - var_name: var3
    output_name: var3_Z
    zbounds: "2. 3."

title: test_none
base_date: "2 1 1 0 0 0"
diag_files:
  - file_name: atmos_daily
    freq: 1 days
    time_units: hours
    unlimdim: time
    module: ocn_mod
    reduction: none
    kind: r4
    varlist:
      - *common_vars
      - var_name: var773
"""

DIAG_TABLE_YAML_ANCHORS2 = """\
common_vars: &common_vars
  - var_name: var0
  - var_name: var1
  - var_name: var2
  - var_name: var3
  - var_name: var4
  - var_name: var3
    output_name: var3_Z
    zbounds: "2. 3."

title: test_none
base_date: "2 1 1 0 0 0"
diag_files:
  - file_name: atmos_daily
    freq: 1 days
    time_units: hours
    unlimdim: time
    module: ocn_mod
    reduction: none
    kind: r4
    varlist:
      - *common_vars
      - var_name: var609
"""

TEST_SIMPLE_YAML_DEFS = {
    'title': 'Very_Important_Title',
    'base_date': '1 1 1 0 0 0',
    'diag_files': [
        {
            'file_name': 'atmos_daily',
            'freq': '1 days',
            'time_units': 'time_units',
            'unlimdim': 'unlimid',
            'module': 'ocn_mod',
            'reduction': 'average',
            'kind': 'r4',
            'varlist': [
                {'var_name': 'tdata'},
                {'var_name': 'vdata'},
                {
                    'var_name': 'tdata',
                    'reduction': 'min',
                    'output_name': 'tdata_min'
                }
            ]
        }
    ]
}

DIAG_TABLE_YAML_SIMPLE = """\
diag_files:
  - file_name: atmos_4xdaily
    freq: 6 hours
    time_units: hours
    unlimdim: time
    module: ocn_mod
    reduction: none
    kind: r4
    varlist:
    - var_name: var773

  - file_name: atmos_daily
    freq: 1 days
    time_units: hours
    unlimdim: time
    module: ocn_mod
    reduction: none
    kind: r4
    varlist:
      - var_name: var609
"""