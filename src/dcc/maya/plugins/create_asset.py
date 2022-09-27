# -*- coding: utf-8 -*-
"""
Documentation: 
"""


# ---------------------------------
# Import Libraries
import os
import sys
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import pyblish.api
import pyblish.util

from dcc.maya.api.cmds import Maya

import maya.cmds as cmds

# ---------------------------------
# Variables


# ---------------------------------
# Start Here
class CreateAsset(pyblish.api.ContextPlugin):
    label = "Get current asset info"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    families = ["asset"]

    def process(self, context):
        ma = Maya()
        selection = ma.selection()

        assert len(selection) == 1, "You should select the asset main group only."
        assert '.' not in selection[0], "You should select the asset main group only."

        asset_name = selection[0]

        # export mesh
        cmds.select(selection, r=1)
        geo_paths = ma.export_selection(asset_dir=None, asset_name=asset_name, export_type=["obj", "abc"], _message=False)
        cmds.select(selection, r=1)

        instance = context.create_instance(
            name=asset_name,
            family="asset",
            file_color_space=ma.get_file_colorspace(),
            renderer=ma.get_renderer(),
            host="maya",
            geo_paths=geo_paths,
            asset_data=ma.get_asset_data(asset_name)
        )


# Main Function
def main():
    pyblish.api.register_host("maya")
    pyblish.api.register_plugin(CreateAsset)

    instance = pyblish.util.collect()[0]

    #pyblish.util.publish()


if __name__ == '__main__':
    main()
