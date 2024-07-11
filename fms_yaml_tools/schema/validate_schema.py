#!/usr/bin/python3
import click
import yaml
import json
#import jsonschema
from jsonschema import validate, ValidationError, SchemaError, Draft7Validator
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
@click.argument("ypath") # This is the path to the file to be validated
@click.argument("spath") # This is the path to the schema to use for validation

def valyaml (ypath,spath,debug,success): #main program
  """ Validates a file (YAML or JSON) based on a schema. \n
      YPATH - Path to the YAML file to be validated against the schema \n
      SPATH - Path to the schema file to use for validation \n

  """
  validate_yaml(ypath, spath, debug, success)

def validate_yaml(ypath, spath, debug, success):
# The debug messages are basically comments showing what the code is doing
  if debug:
    print ("Open "+ypath)
  with open(ypath, 'r') as file:
    if debug:
      print ("Load "+ypath)
    y = yaml.safe_load(file)
  if debug:
    print ("Open "+spath)
  with open(spath, 'r') as f:
    if debug:
      print ("Read "+spath)
    s = f.read()
  if debug:
    print ("Load "+spath)
  schema = json.loads(s)
  if debug:
    print ("Validate "+ypath+" against "+spath)
  try:
    v = validate(instance=y, schema=schema)
  except ValidationError as e:
    print("The following errors have occurred:\n")
    vr = Draft7Validator(schema)
    errors = vr.iter_errors(y)
    i = 1
    for err in errors:
      print("("+str(i)+") "+err.message+"---"+str(err.path))
      i=i+1
    return -1
  if success or debug:
    print (ypath+" was successfully validated against the schema "+spath)

if __name__ == '__main__':
  valyaml(prog_name="valyaml")
