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
import copy
import tempfile
import os
import pathlib
import yaml
from contextlib import contextmanager
from click.testing import CliRunner

from fms_yaml_tools.diag_table.combine_diag_table_yamls import (
    DuplicateFieldError,
    DuplicateKeyError,
    DuplicateOptionalKeyError,
    InconsistentKeys,
    combine_yaml,
    combine_diag_table_yaml,
)
from utils.test_constants import (
    COMBINE_DUPLICATE_DIAG_FILE_SAME_YAML,
    COMBINE_TWO_SIMPLE_YAML_FILES,
    COMBINE_DUPLICATE_DIAG_FILES,
    COMBINE_WITH_ANCHORS,
    COMBINED_WITH_MODULES_BLOCK,
    COMBINE_WITH_SIMPLIFIED_YAML,
    COMBINE_WITH_VARLIST_MODULES,
    DIAG_TABLES_WITH_MODULE_BLOCKS_ANCHORS,
    DIAG_TABLE_YAML_ANCHORS,
    DIAG_TABLE_YAML_ANCHORS2,
    DIAG_TABLE_YAML_INCONSISTENT_KEYS,
    DIAG_TABLE_YAML_WITH_MODULE_BLOCK,
    DIAG_TABLE_YAML_WITH_MODULE_BLOCK2,
    DIAG_TABLE_YAML_WITH_VARLIST,
)


@contextmanager
def test_directory(tmp_path: pathlib.Path):
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


class TestCombineDiagTable(unittest.TestCase):
    # Test with a yaml that does not exist
    def test_missing_yaml(self):
        with self.assertRaises(FileNotFoundError) as context:
            combine_yaml(["file1.yaml"], print)
        self.assertIn("file1.yaml", str(context.exception))

    # Test with a yaml that is not propertly formatted
    def test_bad_formatted_yaml(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                with open("file1.yaml", "w") as file:
                    file.write("title:'this is not going to work'")
                with self.assertRaises(Exception) as context:
                    combine_yaml(["file1.yaml"], print)

                self.assertIn(
                    "ERROR: diagYaml contains incorrectly formatted key value pairs.",
                    str(context.exception),
                )

    # Test with a yaml that is not propertly formatted
    def test_bad_formatted_yaml2(self):
        bad_yaml = 'title: "this is not going to work'

        with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as tmp:
            tmp.write(bad_yaml)
            tmp.flush()

            with self.assertRaises(Exception) as context:
                combine_yaml([tmp.name], print)

            self.assertIn(
                "Please verify that the previous entry", str(context.exception)
            )

    # Test with a yaml that does not include the title and the base_date
    def test_no_title_basedate(self):
        out_dic = DiagYamlFiles()
        diag_yaml = DiagYamlFile()
        diag_files = [DiagFile("atmos_daily", "1 days", "days", "days")]
        diag_yaml.append_to_diag_files(diag_files)
        out_dic.append_yaml([diag_yaml])
        with self.assertRaises(ValueError) as context:
            out_dic.test_combine()

        self.assertIn("base_date or title defined", str(context.exception))

    # Test with two yamls that have the same diag_file, but a different frequency
    def test_same_diag_file_different_keys(self):
        out_dic = DiagYamlFiles()

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        diag_yaml = DiagYamlFile()
        diag_file = DiagFile("atmos_daily", "666 days", "days", "days")
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        with self.assertRaises(DuplicateKeyError):
            out_dic.test_combine()

    # Test two yamls that have the same diag_file, but a different start_time (optional key)
    def test_same_diag_file_different_optional_key(self):
        out_dic = DiagYamlFiles()

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile(
            "atmos_daily", "1 days", "days", "days", "2 1 1 0 0 0"
        )
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        diag_yaml = DiagYamlFile()
        diag_file = DiagFile(
            "atmos_daily", "1 days", "days", "days", "2 2 1 0 0 0"
        )
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        with self.assertRaises(DuplicateOptionalKeyError):
            out_dic.test_combine()

    # Test two yamls that have the same diag_file and a field with the same var_name and module
    # but a different key
    def test_same_fields_different_keys(self):
        out_dic = create_base_input_yaml()
        with self.assertRaises(DuplicateFieldError):
            out_dic.test_combine()

    # Test two yamls that have the same exact diag_file
    def test_combine_duplicate_diag_file_same_yaml(self):
        out_dic = DiagYamlFiles()

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()

        diag_files = [
            DiagFile("atmos_daily", "1 days", "days", "days"),
            DiagFile("atmos_daily", "1 days", "days", "days"),
        ]
        diag_yaml.append_to_diag_files(diag_files)
        out_dic.append_yaml([diag_yaml])

        combined = out_dic.test_combine()
        expected = COMBINE_DUPLICATE_DIAG_FILE_SAME_YAML
        print(combined)
        print(expected)
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test two yamls with different diag_yamls, but the same field
    def test_combine_two_simple_yaml_files(self):
        out_dic = DiagYamlFiles()

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_fields = [DiagField("tdata", "ocn_mod", "average", "r4")]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        diag_yaml = DiagYamlFile()
        diag_file = DiagFile("atmos_8xdaily", "8 hours", "days", "days")
        diag_fields = [DiagField("tdata", "ocn_mod", "average", "r4")]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        combined = out_dic.test_combine()
        expected = COMBINE_TWO_SIMPLE_YAML_FILES
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test two yamls with the same diag_file, but different diag_fields in each (1 is repeated)
    def test_combine_duplicate_diag_files(self):
        out_dic = DiagYamlFiles()

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()

        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_fields = [DiagField("tdata", "ocn_mod", "average", "r4")]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        diag_yaml = DiagYamlFile()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_fields = [
            DiagField("tdata", "ocn_mod", "average", "r4"),
            DiagField("pdata", "ocn_mod", "average", "r4"),
            DiagField("udata", "ocn_mod", "average", "r4"),
        ]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        combined = out_dic.test_combine()
        expected = COMBINE_DUPLICATE_DIAG_FILES
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test two yamls with the same diag_file, they each have same diag_field, but with
    # a different module (should still work)
    def test_combine_duplicate_diag_fields_different_module(self):
        out_dic = create_base_input_yaml(diff_mod="ocn_z_mod")
        combined = out_dic.test_combine()
        expected = get_base_output_dic(mod2="ocn_z_mod")
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test two yamls with the same diag_file, they each have same diag_field, but with
    # a different out_name and reduction
    def test_combine_duplicate_diag_fields(self):
        out_dic = create_base_input_yaml(
            output_name1="tdata_average", output_name2="tdata_min"
        )
        combined = out_dic.test_combine()
        expected = get_base_output_dic(
            output_name1="tdata_average", output_name2="tdata_min"
        )
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test two yamls with the same diag_file, same diag field one has output_name other one doesn't
    def test_combine_duplicate_diag_fields_1outputname(self):
        out_dic = create_base_input_yaml(output_name2="tdata_min")
        combined = out_dic.test_combine()
        expected = get_base_output_dic(output_name2="tdata_min")
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test two yamls with the same diag_file, same field one has outputname, other one doesn't
    def test_combine_duplicate_diag_fields_1outputname_flip(self):
        out_dic = create_base_input_yaml(output_name1="tdata_average")
        combined = out_dic.test_combine()
        expected = get_base_output_dic(output_name1="tdata_average")
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test two yamls with the same diag_file, different fields with the same varname and module,
    # file two has output_name, the other one doesn't
    def test_combine_duplicate_diag_fields_1outputname_mad(self):
        out_dic = create_base_input_yaml(output_name2="tdata")
        with self.assertRaises(DuplicateFieldError):
            out_dic.test_combine()

    # Test two yamls with the same diag_file, different fields with the same varname and module,
    # file one has output_name, the other one doesn't
    def test_combine_duplicate_diag_fields_1outputname_mad_flip(self):
        out_dic = create_base_input_yaml(output_name1="tdata")
        with self.assertRaises(DuplicateFieldError):
            out_dic.test_combine()

    # Test with a yaml that is using anchors
    def test_combine_with_anchors(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # Create a yaml file with anchors
                with open("anchor_file.yaml", "w") as f:
                    f.write(DIAG_TABLE_YAML_ANCHORS)

                with open("anchor_file2.yaml", "w") as f:
                    f.write(DIAG_TABLE_YAML_ANCHORS2)

                input_yamls_names = ["anchor_file.yaml", "anchor_file2.yaml"]
                combined = combine_yaml(input_yamls_names, print)
                expected = COMBINE_WITH_ANCHORS
                self.assertDictEqual(
                    combined,
                    expected,
                    msg="Combined YAML output does not match expected structure.",
                )

    # Test with yamls that define the reduction, kind and module at the file level
    def test_combine_with_simplified_yaml(self):
        out_dic = DiagYamlFiles()

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days",
                             module="ocn_mod", reduction="average", kind="r4")
        diag_fields = [DiagField("tdata", None, None, None)]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days",
                             module="ocn_mod", reduction="average", kind="r4")
        diag_fields = [
            DiagField("vdata", None, None, None),
            DiagField("tdata", None, None, None),
            DiagField("tdata", None, "min", None, output_name="tdata_min")
        ]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        combined = out_dic.test_combine()
        expected = COMBINE_WITH_SIMPLIFIED_YAML
        self.assertDictEqual(
            combined,
            expected,
            msg="Combined YAML output does not match expected structure.",
        )

    # Test with yamls that define the reduction, kind and module at the file level
    def test_combine_with_simplified_yaml_crash(self):
        out_dic = DiagYamlFiles()

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days",
                             module="ocn_mod", reduction="average", kind="r4")
        diag_fields = [DiagField("tdata", None, None, None)]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days",
                             module="ocn_mod", reduction="average", kind="r4")

        # Crash because tdata is defined twice with a different reduction
        # And not output_name
        diag_fields = [
            DiagField("vdata", None, None, None),
            DiagField("tdata", None, "min", None)
        ]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])
        out_dic.append_yaml([diag_yaml])

        with self.assertRaises(DuplicateFieldError):
            out_dic.test_combine()

    # Yaml has both varlist and modules defined in the same file
    def test_combined_with_inconsistent_keys(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # Create a yaml file with anchors
                with open("one.yaml", "w") as f:
                    f.write(DIAG_TABLE_YAML_INCONSISTENT_KEYS)
                with self.assertRaises(InconsistentKeys):
                    combine_yaml(["one.yaml"], print)

    # Combining two files that both use modules
    def test_combined_with_modules_blocks(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                with open("one.yaml", "w") as f:
                    f.write(DIAG_TABLE_YAML_WITH_MODULE_BLOCK)
                with open("two.yaml", "w") as f:
                    f.write(DIAG_TABLE_YAML_WITH_MODULE_BLOCK2)
                combined = combine_yaml(["one.yaml", "two.yaml"], print)
                expected = COMBINED_WITH_MODULES_BLOCK
                self.assertDictEqual(
                    combined,
                    expected,
                    msg="Combined YAML output does not match expected structure.",
                )

    # Combining two different files, one with a varlist and another one with modules
    def test_combine_with_varlist_modules(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                with open("one.yaml", "w") as f:
                    f.write(DIAG_TABLE_YAML_WITH_MODULE_BLOCK)
                with open("two.yaml", "w") as f:
                    f.write(DIAG_TABLE_YAML_WITH_VARLIST)
                combined = combine_yaml(["one.yaml", "two.yaml"], print)
                expected = COMBINE_WITH_VARLIST_MODULES
                self.assertDictEqual(
                    combined,
                    expected,
                    msg="Combined YAML output does not match expected structure.",
                )

    # Combining file that uses anchors and modules
    def test_combine_with_module_blocks_anchors(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                with open("one.yaml", "w") as f:
                    f.write(DIAG_TABLES_WITH_MODULE_BLOCKS_ANCHORS)
                combined = combine_yaml(["one.yaml"], print)
                expected = copy.deepcopy(COMBINE_WITH_VARLIST_MODULES)
                expected['diag_files'].pop(1)
                self.assertDictEqual(
                    combined,
                    expected,
                    msg="Combined YAML output does not match expected structure.",
                )

    # Test the full combine cli
    def test_combine_yaml_cli(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                combined = run_full_combine_cli_test()
                expected = get_base_output_dic(
                    output_name1="tdata_average", output_name2="tdata_min"
                )
                self.assertDictEqual(
                    combined,
                    expected,
                    msg="Combined YAML output does not match expected structure.",
                )

    # Test the full combine cli with a specified output yaml
    def test_combine_yaml_cli_with_outyaml(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                combined = run_full_combine_cli_test(output_yaml_name="out.yaml")
                expected = get_base_output_dic(
                    output_name1="tdata_average", output_name2="tdata_min"
                )
                self.assertDictEqual(
                    combined,
                    expected,
                    msg="Combined YAML output does not match expected structure.",
                )

    # Test the full combine cli with force write
    def test_combine_yaml_cli_force_write(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                combined = run_full_combine_cli_test(use_force=True)
                expected = get_base_output_dic(
                    output_name1="tdata_average", output_name2="tdata_min"
                )
                self.assertDictEqual(
                    combined,
                    expected,
                    msg="Combined YAML output does not match expected structure.",
                )

    # Test the full combine cli without force write and the file already exists!
    def test_combine_yaml_cli_existing_output(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                existing_output = pathlib.Path("diag_table.yaml")
                existing_output.write_text("# existing content\n")

                out_dic = create_base_input_yaml(
                    output_name1="tdata_average", output_name2="tdata_min"
                )
                input_yamls_names = out_dic.create_input()

                runner = CliRunner()
                result = runner.invoke(combine_diag_table_yaml, input_yamls_names)

                assert (
                    result.exit_code != 0
                ), "CLI should fail when output file exists and --force-write is not used"
                assert "File exists" in result.output or isinstance(
                    result.exception, SystemExit
                )


class DiagYamlFiles:
    def __init__(self):
        self.yamls = []

    def append_yaml(self, yamls):
        for yaml_in in yamls:
            self.yamls.append(yaml_in)

    def create_input(self):
        yaml_count = 0
        yaml_file_names = []
        for y in self.yamls:
            filename = f"file_{yaml_count}.yaml"
            file = pathlib.Path(filename)
            file.write_text(yaml.dump(y.to_dict(), sort_keys=False))
            yaml_file_names.append(filename)
            yaml_count += 1
        return yaml_file_names

    def test_combine(self):
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                yaml_file_names = self.create_input()
                combined = combine_yaml(yaml_file_names, print)

        return combined


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


class DiagField:
    def __init__(self, var_name, module, reduction, kind, output_name=None):
        self.var_name = var_name
        self.module = module
        self.reduction = reduction
        self.kind = kind
        self.output_name = output_name

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


def run_full_combine_cli_test(output_yaml_name=None, use_force=False):
    out_dic = create_base_input_yaml(
        output_name1="tdata_average", output_name2="tdata_min"
    )
    input_yamls_names = out_dic.create_input()

    args = input_yamls_names
    if output_yaml_name:
        args += ["--output-yaml", output_yaml_name]
    else:
        output_yaml_name = "diag_table.yaml"

    if use_force:
        args += ["--force-write"]

    runner = CliRunner()
    result = runner.invoke(combine_diag_table_yaml, args)
    assert result.exit_code == 0

    # Check that the out yaml exists
    output_file = pathlib.Path(output_yaml_name)
    assert output_file.exists()

    # Check the contents of the output yaml
    combined = yaml.safe_load(output_file.read_text())

    # Returns a dictionary wit the conents of the output yaml
    return combined


def get_base_output_dic(mod2="ocn_mod", output_name1=None, output_name2=None):
    var1 = {
        "var_name": "tdata",
        "module": "ocn_mod",
        "reduction": "average",
        "kind": "r4",
    }

    var2 = {"var_name": "tdata", "module": mod2, "reduction": "min", "kind": "r4"}

    # Conditionally add Output_name
    if output_name1 is not None:
        var1["output_name"] = output_name1

    if output_name2 is not None:
        var2["output_name"] = output_name2

    expected = {
        "title": "Very_Important_Title",
        "base_date": "1 1 1 0 0 0",
        "diag_files": [
            {
                "file_name": "atmos_daily",
                "freq": "1 days",
                "time_units": "days",
                "unlimdim": "days",
                "varlist": [var1, var2],
            }
        ],
    }

    return expected


def create_base_input_yaml(output_name1=None, output_name2=None, diff_mod="ocn_mod"):
    out_dic = DiagYamlFiles()

    diag_yaml = DiagYamlFile()
    diag_yaml.set_title_basedate()

    diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
    diag_fields = [DiagField("tdata", "ocn_mod", "average", "r4", output_name1)]
    diag_file.append_to_varlist(diag_fields)
    diag_yaml.append_to_diag_files([diag_file])
    out_dic.append_yaml([diag_yaml])

    diag_yaml = DiagYamlFile()
    diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
    diag_fields = [DiagField("tdata", diff_mod, "min", "r4", output_name2)]
    diag_file.append_to_varlist(diag_fields)
    diag_yaml.append_to_diag_files([diag_file])
    out_dic.append_yaml([diag_yaml])

    return out_dic
