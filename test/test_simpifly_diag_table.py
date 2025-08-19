import unittest
import tempfile
import os
import pathlib
from contextlib import contextmanager
from fms_yaml_tools.diag_table.simplify_diag_table import (
    simplify_diag_table
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

class TestSimplifyDiagTable(unittest.TestCase):
    def test_simple_yaml(self):
        pass