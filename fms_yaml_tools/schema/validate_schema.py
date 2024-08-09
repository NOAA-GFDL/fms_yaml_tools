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
import yaml
import json
import sys
from jsonschema import validate, ValidationError, Draft7Validator

""" This program is used for validating a file against a schema.  The
schema is written in JSON format, so the file it is validating must be
in a JSON-like format.  That means that this can be used to validate JSON
or YAML files, but the YAML files must adhere to some of the JSON rules.
The arguments of this program are the path to the file to be validated
which is ypath and the path to the schema file which is spath.
This program uses click for accepting command like arguments and options
and jsonschema to run the validation.
"""


@click.command()
# Debug is used to print more information to the screen.
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
              help="Print steps in the validation")
# This option controls whether or not the program prints a success message
@click.option('--success/--no-show-success', type=click.BOOL, show_default=True, default=False,
              help="Print success message")
# This is the path to the file to be validated
@click.argument("ypath")
# This is the path to the schema to use for validation
@click.argument("spath")
def valyaml(ypath, spath, debug, success):
    """ Validates a file (YAML or JSON) based on a schema. \n
        YPATH - Path to the YAML file to be validated against the schema \n
        SPATH - Path to the schema file to use for validation \n
    """
    validate_yaml(ypath, spath, debug, success)


def validate_yaml(ypath, spath, debug, success):
    # The debug messages are basically comments showing what the code is doing

    # Print only when debug is True
    verboseprint = print if debug else lambda *a, **k: None

    verboseprint("Open "+ypath)
    with open(ypath, 'r') as file:
        verboseprint("Load "+ypath)
        y = yaml.safe_load(file)

    verboseprint("Open "+spath)
    with open(spath, 'r') as f:
        verboseprint("Read "+spath)
        s = f.read()

    verboseprint("Load "+spath)
    schema = json.loads(s)
    verboseprint("Validate "+ypath+" against "+spath)

    try:
        validate(instance=y, schema=schema)
    except ValidationError:
        print("The following errors have occurred:\n")
        vr = Draft7Validator(schema)
        errors = vr.iter_errors(y)
        i = 1
        for err in errors:
            print("(" + str(i) + ") " + err.message + "---" + str(err.path))
            i = i + 1
        sys.exit("ERROR: "+ ypath + " is not a valid yaml")
    if success or debug:
        print(ypath+" was successfully validated against the schema "+spath)


if __name__ == '__main__':
    valyaml(prog_name="valyaml")
