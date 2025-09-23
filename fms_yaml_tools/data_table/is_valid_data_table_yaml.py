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

import click
import importlib.resources
from fms_yaml_tools.schema.validate_schema import validate_yaml


@click.command()
# Debug is used to print more information to the screen.
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the validation")
# This option controls whether or not the program prints a success message
@click.option('--success/--no-show-success', type=click.BOOL, show_default=True, default=False,
              help="Print success message")
# This is the path to the file to be validated
@click.argument("ypath")
def validate_data_yaml(ypath, debug, success):
    """ Validates a data_table.yaml based on a schema to check for any errors. \n
        YPATH - Path to the data_table.yaml file to be validated against the schema \n
    """
    schema_path = importlib.resources.files('fms_yaml_tools') / "schema/gfdl_msd_schemas/FMS/data_table.json"
    validate_yaml(ypath, schema_path, debug, success)


if __name__ == "__main__":
    validate_data_yaml(prog_name="validate_data_yaml")
