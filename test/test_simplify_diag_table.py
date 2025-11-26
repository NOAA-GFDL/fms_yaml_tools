import unittest
import tempfile
import os
import pathlib
import yaml
from contextlib import contextmanager
from click.testing import CliRunner
from fms_yaml_tools.diag_table.simplify_diag_table import (
    construct_yaml,
    dump_output_yaml,
    simplify_diag_table,
    parse_yaml
)
from utils.test_classes import (
    DiagField,
    DiagFile,
    DiagYamlFile
)
from utils.test_constants import (
    TEST_SIMPLIFY_DIAG_TABLE_1MOD,
    TEST_SIMPLIFY_DIAG_TABLE_MULTIPLE_MODS
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


class TestSimplifyDiagTable(unittest.TestCase):
    def test_simple_yaml_1mod(self):
        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_fields = [
            DiagField("tdata", "ocn_mod", "average", "r4"),
            DiagField("pdata", "ocn_mod", "average", "r4"),
            DiagField("udata", "ocn_mod", "average", "r4"),
        ]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])

        assert_yaml_output_matches(self, diag_yaml, TEST_SIMPLIFY_DIAG_TABLE_1MOD)

    def test_simple_yaml_multiple_mods(self):
        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_fields = [
            DiagField("tdata", "ocn_mod", "average", "r4"),
            DiagField("pdata", "ocn_mod", "average", "r4"),
            DiagField("udata", "ocn_mod", "average", "r4"),
            DiagField("tdata", "ocn_z_mod", "average", "r4"),
            DiagField("pdata", "ocn_z_mod", "average", "r4"),
            DiagField("udata", "ocn_z_mod", "average", "r4"),
        ]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])

        assert_yaml_output_matches(self, diag_yaml, TEST_SIMPLIFY_DIAG_TABLE_MULTIPLE_MODS)

    def test_yaml_with_no_diag_fields(self):
        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days", add_varlist=False)
        diag_yaml.append_to_diag_files([diag_file])

        assert_yaml_output_matches(self, diag_yaml, diag_yaml.to_dict())

    def test_missing_required_key(self):
        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_fields = [
            DiagField("tdata", "ocn_mod", "average", None)
        ]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])

        with self.assertRaises(KeyError) as context:
            construct_yaml(diag_yaml.to_dict())

        self.assertIn(
            "Missing required key: kind", str(context.exception),
            "KeyError did not mention missing 'kind'"
        )

    def test_simplify_diag_table_cli(self):
        diag_yaml = DiagYamlFile()
        diag_yaml.set_title_basedate()
        diag_file = DiagFile("atmos_daily", "1 days", "days", "days")
        diag_fields = [
            DiagField("tdata", "ocn_mod", "average", "r4"),
            DiagField("pdata", "ocn_mod", "average", "r4"),
            DiagField("udata", "ocn_mod", "average", "r4"),
        ]
        diag_file.append_to_varlist(diag_fields)
        diag_yaml.append_to_diag_files([diag_file])

        run_simplify_diag_table_cli(self, diag_yaml.to_dict(), TEST_SIMPLIFY_DIAG_TABLE_1MOD)

    def test_bad_yaml(self):
        with tempfile.TemporaryDirectory() as testdir:
            with create_directory(testdir):
                with open("file1.yaml", "w") as file:
                    file.write("title:'this is not going to work'")

                with open("file1.yaml", "r") as file:
                    with self.assertRaises(Exception) as context:
                        parse_yaml(file)

        self.assertIn(
            "incorrectly formatted key value pairs",
            str(context.exception),
            msg="Expected error message about bad YAML formatting not found."
        )

    def test_bad_yaml_2(self):
        with tempfile.TemporaryDirectory() as testdir:
            with create_directory(testdir):
                with open("file1.yaml", "w") as file:
                    file.write('title: "this is not going to work')

                with open("file1.yaml", "r") as file:
                    with self.assertRaises(Exception) as context:
                        parse_yaml(file)

        self.assertIn(
            "Please verify that the previous entry",
            str(context.exception),
            msg="Expected error message about bad YAML formatting not found."
        )


def run_simplify_diag_table_cli(testcase, diag_yaml, expected_dict):
    with tempfile.TemporaryDirectory() as testdir:
        with create_directory(testdir):
            input_yamls_name = "input.yaml"
            with open(input_yamls_name, "w") as f:
                yaml.dump(diag_yaml, f, sort_keys=False)

            args = input_yamls_name
            runner = CliRunner()
            result = runner.invoke(simplify_diag_table, args)
            assert result.exit_code == 0

            output_path = os.path.join(testdir, "diag_table.yaml")
            testcase.assertTrue(os.path.exists(output_path), "Output yaml was not created")

            with open(output_path, "r") as f:
                out_yaml = yaml.safe_load(f)

            testcase.assertDictEqual(
                out_yaml,
                expected_dict,
                msg="Output YAML output does not match expected structure.",
            )


def assert_yaml_output_matches(testcase, diag_yaml, expected_dict):
    simple_yaml = construct_yaml(diag_yaml.to_dict())
    testcase.assertDictEqual(
        simple_yaml,
        expected_dict,
        msg="Simplified YAML output does not match expected structure.",
    )

    # Compare dumped YAML file
    with tempfile.TemporaryDirectory() as testdir:
        with create_directory(testdir):
            dump_output_yaml(simple_yaml, "diag_table.yaml", True)

            output_path = os.path.join(testdir, "diag_table.yaml")
            testcase.assertTrue(os.path.exists(output_path), "Output yaml was not created")

            with open(output_path, "r") as f:
                out_yaml = yaml.safe_load(f)

            testcase.assertDictEqual(
                out_yaml,
                expected_dict,
                msg="Output YAML output does not match expected structure.",
            )
