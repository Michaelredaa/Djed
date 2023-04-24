# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, ]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

# ---------------------------------
# Variables
djed_order = 1.10
djed_annotation = "To validate the selected asset"
djed_icon = "pyblish.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""

# ---------------------------------
# Start Here
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
    plugin_path = DJED_ROOT + r"djed/dcc/maya/plugins"

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


def left_click():
    process()


def right_click():
    pass


def double_click():
    pass

