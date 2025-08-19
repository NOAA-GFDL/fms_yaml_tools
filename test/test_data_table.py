import unittest
import tempfile
import os
import pathlib
from contextlib import contextmanager

from fms_yaml_tools.data_table.data_table_to_yaml import DataType

EXAMPLE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'examples'))


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


class TestDataTable(unittest.TestCase):

    def test_DataType(self):
        """Test that DataTable returns itself.
           Inputs: None -- Taking defaults
        """
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # Create empty data_table file
                with open('data_table', 'w'):
                    pass
                test_data_type = DataType()
            self.assertIsInstance(test_data_type, DataType)

    def test_DataType_no_data_table(self):
        """Test that the DataType raises
           raises FileNotFoundError"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # No data_table
                with self.assertRaises(FileNotFoundError):
                    DataType()

    def test_DataType_give_data_table_file(self):
        """Thest the ability to give a path
           to a data_table file"""
        # Path to example data
        DataType(os.path.join(EXAMPLE_DIR, 'data_table'))

    def test_DataType_give_file_no_exist(self):
        """Check if FileNotFoundError raised if given
           a data_table file that doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            DataType('does_not_exist')

    def test_DataType_out_file(self):
        """Test if able to give an output yaml file"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                test_dt = DataType(os.path.join(EXAMPLE_DIR, 'data_table'),
                                   'outfile.yaml')
                self.assertEqual(test_dt.yaml_table_file, 'outfile.yaml')

    def test_DataType_out_dir_not_exist(self):
        """Test if the output dir does not exist and that it
           raises FileNotFoundError"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                with self.assertRaises(NotADirectoryError):
                    DataType(os.path.join(EXAMPLE_DIR, 'data_table'),
                             'does_not_exist/outfile.yaml')

    def test_read_data_table(self):
        """Test the reading of a data table
        """
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                with open('data_table', 'w') as f:
                    f.write("This is a test line")
                test_data_type = DataType()
                test_data_type.read_data_table()
                self.assertEqual(test_data_type.data_table_content,
                                 ["This is a test line"])

    def test_parse_data_table(self):
        """Test parsing data_table"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                test_dt = DataType(os.path.join(EXAMPLE_DIR, 'data_table'))
                test_dt.read_data_table()
                test_dt.parse_data_table()

        # Verification Data
        # TODO: generate this programmatically, if possible
        dt_verify = [{'grid_name': 'ICE',
                      'fieldname_in_model': 'sic_obs',
                      'factor': 0.01,
                      'override_file':
                          [{'file_name': 'INPUT/hadisst_ice.data.nc',
                            'fieldname_in_file': 'ice',
                            'interp_method': 'bilinear'}]},
                     {'grid_name': 'ICE',
                      'fieldname_in_model': 'sit_obs',
                      'factor': 2.0},
                     {'grid_name': 'ICE',
                      'fieldname_in_model': 'sst_obs',
                      'factor': 1.0,
                      'override_file':
                          [{'file_name': 'INPUT/hadisst_sst.data.nc',
                            'fieldname_in_file': 'sst',
                            'interp_method': 'bilinear'}]},
                     {'grid_name': 'LND',
                      'fieldname_in_model': 'phot_co2',
                      'factor': 1e-06,
                      'override_file':
                          [{'file_name': 'INPUT/co2_data.nc',
                            'fieldname_in_file': 'co2',
                            'interp_method': 'bilinear'}]},
                     {'grid_name': 'LND',
                      'fieldname_in_model': 'some_var',
                      'factor': 1.0,
                      'subregion':
                          [{'lon_start': 10.0,
                            'lon_end': 20.0,
                            'lat_start': 80.0,
                            'lat_end': 100.0,
                            'type': 'inside_region'}],
                      'override_file':
                          [{'file_name': 'INPUT/no_file.nc',
                            'fieldname_in_file': 'var',
                            'interp_method': 'bilinear'}]},
                     {'grid_name': 'OCN',
                      'fieldname_in_model': 'ocn_var1',
                      'factor': 2.1,
                      'subregion':
                          [{'lon_start': 10.0,
                            'lon_end': 20.0,
                            'lat_start': 80.0,
                            'lat_end': 100.0,
                            'type': 'outside_region'}],
                      'override_file':
                          [{'file_name': 'INPUT/ocean_var1.nc',
                            'fieldname_in_file': 'var1',
                            'interp_method': 'bicubic'}]},
                     {'grid_name': 'ATM',
                      'fieldname_in_model': 'atm_var',
                      'factor': 1.1,
                      'override_file':
                          [{'file_name': 'INPUT/atm.data.nc',
                            'fieldname_in_file': 'atm',
                            'interp_method': 'bilinear'}]},
                     {'grid_name': 'ATM',
                      'fieldname_in_model': 'atm_var1',
                      'factor': 1.2,
                      'override_file':
                          [{'file_name': 'INPUT/atm1.data.nc',
                            'fieldname_in_file': 'atm1',
                            'interp_method': 'none'}]}]
        # Verify parse done correctly
        self.assertListEqual(test_dt.data_type['data_table'],
                             dt_verify)


if __name__ == '__main__':
    unittest.main()
