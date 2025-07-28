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

import unittest
import tempfile
import os
import pathlib
import yaml
from contextlib import contextmanager
from click.testing import CliRunner
from fms_yaml_tools.diag_table.is_valid_diag_table_yaml import (
   validate_diag_yaml,
)
from fms_yaml_tools.diag_table.test_constants import (
    COMBINE_TWO_SIMPLE_YAML_FILES,
    COMBINE_DUPLICATE_DIAG_FILES,
    COMBINE_WITH_ANCHORS,
    COMBINED_WITH_MODULES_BLOCK,
    COMBINE_WITH_SIMPLIFIED_YAML,
    COMBINE_WITH_VARLIST_MODULES,
    DIAG_TABLES_WITH_MODULE_BLOCKS_ANCHORS,
)


@contextmanager
def create_directory(tmp_path: pathlib.Path):
    """Set the cwd to the path

    Args:
        tmp_path (Path): The path to use

    Yields:
        None
    """
    origin = pathlib.Path().absolute()
    try:
        os.chdir(tmp_path)
        yield
    finally:
        os.chdir(origin)


class ValidateDiagYaml(unittest.TestCase):
    # Test with a yaml that does not exist
    def _run_yaml_dict_test(self, yaml_input):
        """Run CLI validation on either a dict or a YAML string."""
        with tempfile.TemporaryDirectory() as testdir:
            with create_directory(testdir):
                file_path = os.path.join(testdir, "file1.yaml")

                if isinstance(yaml_input, dict):
                    yaml_string = yaml.dump(
                        yaml_input,
                        sort_keys=False,
                        default_flow_style=False
                    )
                elif isinstance(yaml_input, str):
                    yaml_string = yaml_input
                else:
                    raise TypeError("yaml_input must be a dict or YAML string")

                with open(file_path, "w") as file:
                    file.write(yaml_string)

                args = [file_path, "--debug", "--success"]
                runner = CliRunner()
                result = runner.invoke(validate_diag_yaml, args)

                self.assertEqual(
                    result.exit_code,
                    0,
                    msg=f"CLI failed:\n{result.output}"
                )
    # These are all testing the valid output from test_combine_diag_table
    def test_valid_diag_yaml_two_simple_yaml_files(self):
        self._run_yaml_dict_test(COMBINE_TWO_SIMPLE_YAML_FILES)

    def test_valid_diag_yaml_duplicate_diag_files(self):
        self._run_yaml_dict_test(COMBINE_DUPLICATE_DIAG_FILES)

    def test_valid_diag_yaml_with_anchors(self):
        self._run_yaml_dict_test(COMBINE_WITH_ANCHORS)

    def test_valid_diag_yaml_with_modules_block(self):
        self._run_yaml_dict_test(COMBINED_WITH_MODULES_BLOCK)

    def test_valid_diag_yaml_with_simplified_yaml(self):
        self._run_yaml_dict_test(COMBINE_WITH_SIMPLIFIED_YAML)

    def test_valid_diag_yaml_with_varlist_modules(self):
        self._run_yaml_dict_test(COMBINE_WITH_VARLIST_MODULES)

    def test_valid_diag_yaml_with_anchors_raw(self):
        self._run_yaml_dict_test(DIAG_TABLES_WITH_MODULE_BLOCKS_ANCHORS)

    #TODO Negative tests