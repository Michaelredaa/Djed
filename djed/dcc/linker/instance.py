# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import site
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))

site.addsitedir(DJED_ROOT.joinpath('venv/python/Lib/site-packages').as_posix())

import pyblish.api

def create_instance(data):
    context = pyblish.api.Context()
    instance = context.create_instance(**data)
    return instance

if __name__ == '__main__':
    print(__name__)
