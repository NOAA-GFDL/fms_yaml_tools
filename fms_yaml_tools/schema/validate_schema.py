#!/usr/bin/python3
import click
import yaml
import json
from jsonschema import validate, ValidationError, SchemaError

@click.command()
@click.option('--debug/--no-debug', type=click.BOOL, show_default=True, default=False,
   help="Print steps in the validation")
@click.option('--success/--no-show-success', type=click.BOOL, show_default=True, default=False,
   help="Print success message")
@click.argument("ypath")
@click.argument("spath")

def valyaml (ypath,spath,debug,success):
  """ Validates a file (YAML or JSON) based on a schema. \n
      YPATH - Path to the YAML file to be validated against the schema \n
      SPATH - Path to the schema file to use for validation \n

  """
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
  validate(instance=y, schema=schema)
  if success or debug:
    print (ypath+" was successfully validated against the schema "+spath)

if __name__ == '__main__':
  valyaml(prog_name="valyaml")
