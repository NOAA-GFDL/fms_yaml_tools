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
