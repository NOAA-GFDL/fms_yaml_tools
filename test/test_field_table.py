import unittest
import tempfile
import os
import pathlib
from contextlib import contextmanager

from fms_yaml_tools.field_table.field_table_to_yaml import Field
from fms_yaml_tools.field_table.field_table_to_yaml import FieldYaml
from collections import OrderedDict

EXAMPLE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'examples'))


@contextmanager
def test_directory(path: pathlib.Path):
    """Set the cwd to the path

    Args:
        path (Path): The path to use

    Yields:
        None
    """

    origin = pathlib.Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


class TestFieldTable(unittest.TestCase):

    def test_FieldYaml(self):
        """Test that FieldYaml returns itself.
        """
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # Create empty data_table file
                with open('field_table', 'w'):
                    pass
                test_field_yaml = FieldYaml('field_table')
            self.assertIsInstance(test_field_yaml, FieldYaml)

    def test_FieldYaml_no_table(self):
        """Test that the FieldYaml raises
           raises FileNotFoundError"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # No data_table
                with self.assertRaises(FileNotFoundError):
                    FieldYaml("")

    def test_FieldYaml_path(self):
        """Test the ability to give a path
           to a field_table file"""
        # Path to example data
        FieldYaml(os.path.join(EXAMPLE_DIR, 'field_table'))

    def test_FieldYaml_output(self):
        """Test that FieldYaml outputs to a given filename/path"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # Create empty data_table file
                path = os.path.join(EXAMPLE_DIR, 'field_table')
                fy = FieldYaml(path)
                fy.main()
                fy.writeyaml('output-test.yaml', True)

    def test_FieldYaml_file_not_found(self):
        """Check if FileNotFoundError raised if given
           a data_table file that doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            FieldYaml('does_not_exist')

    def test_FieldYaml_conversion(self):
        """Test conversion of example file
           Checks for correct length of output yaml"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                path = os.path.join(EXAMPLE_DIR, 'field_table')
                fy = FieldYaml(path)
                fy.main()
                fy.writeyaml("field_table.yaml", True)
                with open(path+'.yaml', 'r') as fp:
                    lines = len(fp.readlines())
                    self.assertEqual(lines, 624)

    def test_FieldYaml_overwrite(self):
        """Test overwrites of output file
           Checks if overwrites a blank file with --force, and then checks if it errors out without it"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                path = os.path.join(EXAMPLE_DIR, 'field_table')
                fy = FieldYaml(path)
                fy.main()
                with open(path+'.yaml', 'w') as fp:
                    fp.write('')
                fy.writeyaml("field_table.yaml", True)
                with open(path+'.yaml', 'r') as fp:
                    lines = len(fp.readlines())
                    self.assertEqual(lines, 624)
                with self.assertRaises(FileExistsError):
                    fy.writeyaml("field_table.yaml", False)


    def test_FieldYaml_parse_table(self):
        """Test the reading of a field table
        """
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                with open('field_table', 'w') as f:
                    f.write("\"TRACER\", \"atmos_mod\", \"liq_wat\"\n")
                    f.write("\t\"longname\", \"cloud liquid specific humidity\"")
                    f.write("\t\"units\", \"kg/kg\" /")
                fy = FieldYaml('field_table')
                fy.main()
                ref_dict = {'field_table':
                            [OrderedDict([('field_type', 'tracer'),
                                          ('modlist',
                                           [OrderedDict([('model_type', 'atmos_mod'),
                                                         ('varlist',
                                                         [OrderedDict([('variable', 'liq_wat'),
                                                                       ('longname', 'fm_yaml_null'),
                                                                       ('subparams0',
                                                                       [OrderedDict([
                                                                            ('cloud liquid specific humidityunits',
                                                                             'kg/kg')])])])])])])])]}
                # Verify parse done correctly
                self.assertDictEqual(fy.lists_wh_yaml, ref_dict)


if __name__ == '__main__':
    unittest.main()
