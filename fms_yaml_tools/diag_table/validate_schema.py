#!/usr/bin/python3
import yaml
import json
from jsonschema import validate, ValidationError, SchemaError

with open("diag_table.yaml", 'r') as file:
  y = yaml.safe_load(file)
with open("schema.diag", 'r') as f:
  s = f.read()
schema = json.loads(s)
validate(instance=y, schema=schema)

