# -*- coding: utf-8 -*-
"""
Documentation:
"""
# ---------------------------------
# MetaData
_annotation = "Validate mesh "
_icon = "updateSubstance.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------
# import libraries

import os
import sys
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [
    DJED_ROOT.as_posix(),
    DJED_ROOT.joinpath('src').as_posix(),
    DJED_ROOT.joinpath('venv/python39/Lib/site-packages').as_posix()
]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import pyblish.api, pyblish_lite, pyblish_maya

from dcc.maya.plugins import (
    CollectMesh,
    ValidateNormals,
    ValidateUVSets,
    ValidateTopology,
    ValidateUVBoarders,
    ValidateShadingGroups,
    ValidateMultipleMaterialAssign,
    ValidateNamespaces,
    ValidateNaming,
    ExtractModel,

)


def process(**kwargs):
    plugin_path = os.getenv('DJED_ROOT') + r"src/dcc/maya/plugins"

    pyblish.util.plugin.deregister_all_plugins()
    # pyblish.api.deregister_plugin_path(plugin_path)
    # pyblish.api.register_plugin_path(plugin_path)
    # pyblish.api.plugins_by_family()

    pyblish.api.register_host("maya")
    pyblish.api.register_gui("pyblish_lite")
    # pyblish.api.register_gui("pyblish_qml")

    # options
    pyblish_lite.settings.WindowTitle = "Publish Geometry"
    pyblish_lite.settings.InitialTab = "overview"  # "artist", "overview" and "terminal"
    pyblish_lite.settings.UseLabel = True
    pyblish_lite.settings.TerminalLoglevel = 1

    # plugins = pyblish.api.discover()
    CollectMesh.external_data = kwargs

    plugins = [
        CollectMesh,
        ValidateNormals,
        ValidateUVSets,
        ValidateTopology,
        ValidateUVBoarders,
        ValidateShadingGroups,
        ValidateMultipleMaterialAssign,
        ValidateNamespaces,
        ValidateNaming,
        ExtractModel,

    ]

    for _plugin in plugins:
        pyblish.api.register_plugin(_plugin)

    pyblish_maya.show()


if __name__ == '__main__':
    process()
