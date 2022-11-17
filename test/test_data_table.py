import unittest
import tempfile
import os
import pathlib
from contextlib import contextmanager

from fms_yaml_tools.data_table.data_table_to_yaml import DataType

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
        dt_verify = [{'gridname': 'ICE',
                      'fieldname_code': 'sic_obs',
                      'fieldname_file': 'ice',
                      'file_name': 'INPUT/hadisst_ice.data.nc',
                      'interpol_method': 'bilinear',
                      'factor': 0.01},
                     {'gridname': 'ICE',
                      'fieldname_code': 'sit_obs',
                      'factor': 2.0},
                     {'gridname': 'ICE',
                      'fieldname_code': 'sst_obs',
                      'fieldname_file': 'sst',
                      'file_name': 'INPUT/hadisst_sst.data.nc',
                      'interpol_method': 'bilinear',
                      'factor': 1.0},
                     {'gridname': 'LND',
                      'fieldname_code': 'phot_co2',
                      'fieldname_file': 'co2',
                      'file_name': 'INPUT/co2_data.nc',
                      'interpol_method': 'bilinear',
                      'factor': 1e-06},
                     {'gridname': 'LND',
                      'fieldname_code': 'some_var',
                      'fieldname_file': 'var',
                      'file_name': 'INPUT/no_file.nc',
                      'interpol_method': 'default',
                      'factor': 1.0,
                      'lon_start': 10.0,
                      'lon_end': 20.0,
                      'lat_start': 80.0,
                      'lat_end': 100.0,
                      'region_type': 'inside_region'},
                     {'gridname': 'OCN',
                      'fieldname_code': 'ocn_var1',
                      'fieldname_file': 'var1',
                      'file_name': 'INPUT/ocean_var1.nc',
                      'interpol_method': 'bicubic',
                      'factor': 2.1,
                      'lon_start': 10.0,
                      'lon_end': 20.0,
                      'lat_start': 80.0,
                      'lat_end': 100.0,
                      'region_type': 'outside_region'},
                     {'gridname': 'ATM',
                      'fieldname_code': 'atm_var',
                      'fieldname_file': 'atm',
                      'file_name': 'INPUT/atm.data.nc',
                      'interpol_method':
                      'bilinear',
                      'factor': 1.1},
                     {'gridname': 'ATM',
                      'fieldname_code': 'atm_var1',
                      'fieldname_file': 'atm1',
                      'file_name': 'INPUT/atm1.data.nc',
                      'interpol_method': 'none',
                      'factor': 1.2}]
        # Verify parse done correctly
        self.assertListEqual(test_dt.data_type['data_table'],
                             dt_verify)


if __name__ == '__main__':
    unittest.main()
