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

# Constants to use for tests

# Expected output for `test_duplicate_diag_file_same_yaml`
COMBINE_DUPLICATE_DIAG_FILE_SAME_YAML = {
    "title": "Very_Important_Title",
    "base_date": "1 1 1 0 0 0",
    "diag_files": [
        {
            "file_name": "atmos_daily",
            "freq": "1 days",
            "time_units": "days",
            "unlimdim": "days",
            "varlist": [],
        }
    ],
}

# Expected output for `test_combine_duplicate_diag_files`
COMBINE_TWO_SIMPLE_YAML_FILES = {
    "title": "Very_Important_Title",
    "base_date": "1 1 1 0 0 0",
    "diag_files": [
        {
            "file_name": "atmos_daily",
            "freq": "1 days",
            "time_units": "days",
            "unlimdim": "days",
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
            "time_units": "days",
            "unlimdim": "days",
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

# Expected output for `test_combine_duplicate_diag_files`
COMBINE_DUPLICATE_DIAG_FILES = {
    "title": "Very_Important_Title",
    "base_date": "1 1 1 0 0 0",
    "diag_files": [
        {
            "file_name": "atmos_daily",
            "freq": "1 days",
            "time_units": "days",
            "unlimdim": "days",
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

# Expected output for `test_combine_with_anchors`
COMBINE_WITH_ANCHORS = {
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

# Input yaml for `test_combine_with_anchors`
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

# Input yaml for `test_combine_with_anchors`
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

# Expected output for `test_simple_yaml_defs`
COMBINE_WITH_SIMPLIFIED_YAML = {
    'title': 'Very_Important_Title',
    'base_date': '1 1 1 0 0 0',
    'diag_files': [
        {
            'file_name': 'atmos_daily',
            'freq': '1 days',
            'time_units': 'days',
            'unlimdim': 'days',
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

# Expected output for `test_combined_with_modules_blocks`
COMBINED_WITH_MODULES_BLOCK = {
    'title': 'test_none',
    'base_date': '2 1 1 0 0 0',
    'diag_files': [
        {
            'file_name': 'test_4xdaily',
            'freq': '6 hours',
            'time_units': 'hours',
            'unlimdim': 'time',
            'reduction': 'none',
            'kind': 'r4',
            'modules': [
                {
                    'module': 'radiation_mod',
                    'varlist': [
                        {'var_name': 'var0'},
                        {'var_name': 'var1'}
                    ]
                },
                {
                    'module': 'some_other_mod',
                    'varlist': [
                        {'var_name': 'var3'}
                    ]
                },
                {
                    'module': 'happy_mod',
                    'varlist': [
                        {'var_name': 'var4'}
                    ]
                }
            ]
        }
    ]
}

# Input yaml for `test_combined_with_inconsistent_keys`
DIAG_TABLE_YAML_INCONSISTENT_KEYS = """
title: test_invalid
base_date: 2 1 1 0 0 0

diag_files:
  - file_name: atmos_daily
    freq: 1 days
    time_units: hours
    unlimdim: time
    module: ocn_mod
    reduction: none
    kind: r4
    varlist:
      - var_name: temp
      - var_name: salt
    modules:
      - module_name: ocn_mod
        varlist:
          - var_name: u
          - var_name: v
"""

# Input yaml for `test_combined_with_modules_blocks`
DIAG_TABLE_YAML_WITH_MODULE_BLOCK = """
title: test_none
base_date: 2 1 1 0 0 0
diag_files:
- file_name: test_4xdaily
  freq: 6 hours
  time_units: hours
  unlimdim: time
  reduction: none
  kind: r4
  modules:
  - module: radiation_mod
    varlist:
    - var_name: var0
  - module: some_other_mod
    varlist:
    - var_name: var3
"""

# Input yaml for `test_combined_with_modules_blocks`
DIAG_TABLE_YAML_WITH_MODULE_BLOCK2 = """
title: test_none
base_date: 2 1 1 0 0 0
diag_files:
- file_name: test_4xdaily
  freq: 6 hours
  time_units: hours
  unlimdim: time
  reduction: none
  kind: r4
  modules:
  - module: radiation_mod
    varlist:
    - var_name: var1
  - module: happy_mod
    varlist:
    - var_name: var4
"""

# Input yaml for test_combine_with_varlist_modules
DIAG_TABLE_YAML_WITH_VARLIST = """
title: test_none
base_date: 2 1 1 0 0 0
diag_files:
- file_name: test_daily
  freq: 1 days
  time_units: hours
  unlimdim: time
  reduction: none
  kind: r4
  module: radiation_mod
  varlist:
  - var_name: var1
  - var_name: var4
"""

# Expected output for `test_combine_with_varlist_modules`
COMBINE_WITH_VARLIST_MODULES = {
    'title': 'test_none',
    'base_date': '2 1 1 0 0 0',
    'diag_files': [
        {
            'file_name': 'test_4xdaily',
            'freq': '6 hours',
            'time_units': 'hours',
            'unlimdim': 'time',
            'reduction': 'none',
            'kind': 'r4',
            'modules': [
                {
                    'module': 'radiation_mod',
                    'varlist': [{'var_name': 'var0'}]
                },
                {
                    'module': 'some_other_mod',
                    'varlist': [{'var_name': 'var3'}]
                }
            ]
        },
        {
            'file_name': 'test_daily',
            'freq': '1 days',
            'time_units': 'hours',
            'unlimdim': 'time',
            'reduction': 'none',
            'kind': 'r4',
            'module': 'radiation_mod',
            'varlist': [
                {'var_name': 'var1'},
                {'var_name': 'var4'}
            ]
        }
    ]
}

# Input for `test_combine_with_modules_block`
DIAG_TABLES_WITH_MODULE_BLOCKS_ANCHORS = """
radiation_mod: &radiation_mod
  module: radiation_mod
  varlist:
    - var_name: var0

some_other_mod: &some_other_mod
  module: some_other_mod
  varlist:
    - var_name: var3

title: test_none
base_date: 2 1 1 0 0 0
diag_files:
  - file_name: test_4xdaily
    freq: 6 hours
    time_units: hours
    unlimdim: time
    reduction: none
    kind: r4
    modules:
      - *radiation_mod
      - *some_other_mod
"""

TEST_SIMPLIFY_DIAG_TABLE_1MOD = {
    'title': 'Very_Important_Title',
    'base_date': '1 1 1 0 0 0',
    'diag_files': [
        {
            'file_name': 'atmos_daily',
            'freq': '1 days',
            'time_units': 'days',
            'unlimdim': 'days',
            'varlist': [
                {'var_name': 'tdata'},
                {'var_name': 'pdata'},
                {'var_name': 'udata'}
            ],
            'kind': 'r4',
            'reduction': 'average',
            'module': 'ocn_mod'
        }
    ]
}

TEST_SIMPLIFY_DIAG_TABLE_MULTIPLE_MODS = {
    'title': 'Very_Important_Title',
    'base_date': '1 1 1 0 0 0',
    'diag_files': [
        {
            'file_name': 'atmos_daily',
            'freq': '1 days',
            'time_units': 'days',
            'unlimdim': 'days',
            'kind': 'r4',
            'reduction': 'average',
            'modules': [
                {
                    'module': 'ocn_mod',
                    'varlist': [
                        {'var_name': 'tdata'},
                        {'var_name': 'pdata'},
                        {'var_name': 'udata'}
                    ]
                },
                {
                    'module': 'ocn_z_mod',
                    'varlist': [
                        {'var_name': 'tdata'},
                        {'var_name': 'pdata'},
                        {'var_name': 'udata'}
                    ]
                }
            ]
        }
    ]
}
