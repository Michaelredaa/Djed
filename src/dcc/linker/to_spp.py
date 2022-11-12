# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))

##########################
import importlib

import dcc.spp.plugins.load_asset
importlib.reload(dcc.spp.plugins.load_asset)
############################

from dcc.linker.instance import create_instance
from dcc.spp.plugins.load_asset import LoadAsset
from dcc.spp.plugins.update_asset import UpdateAsset


def send_to_spp(data):
    instance = create_instance(data)
    LoadAsset().process(instance)

def update_spp(data):
    instance = create_instance(data)
    UpdateAsset().process(instance)

# Main function
def main():
    pass


if __name__ == '__main__':
    main()
    print(__name__)
