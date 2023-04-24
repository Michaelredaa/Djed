# -*- coding: utf-8 -*-
"""
Documentation: 
"""
import json

# ---------------------------------
# Import Libraries
import os
import sys
import site
from pathlib import Path


DJED_ROOT = Path(os.getenv("DJED_ROOT"))

site.addsitedir(DJED_ROOT.joinpath('venv', 'python', 'Lib', 'site-packages').as_posix())

from jsonschema import validate, ValidationError

# ---------------------------------
# Variables



# ---------------------------------
# Start Here
def validate_data(data, schema_name):
    # Validate against schema
    schema_file = DJED_ROOT.joinpath('djed/schema', f'{schema_name}.json')

    if not schema_file.is_file():
        raise FileExistsError(f'File not exists with schema name `{schema_name}`')

    with open(schema_file, 'r') as f:
        schema_data = json.load(f)

    try:
        validate(data, schema_data)
    except ValidationError as e:
        raise ValueError(f'JSON data of `{data}` validation failed: {e}')


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
