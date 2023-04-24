# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
import re

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, ]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.maya.api.cmds import Maya
from dcc.linker.to_spp import update_spp


# ---------------------------------
# Variables
djed_order = 2.10
djed_annotation = "Update selection to substance painter current session"
djed_icon = "updateSubstance.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""


# ---------------------------------
# Start Here


def left_click():
    ma = Maya()
    asset_name = ma.selection()[0]
    mesh_path = ma.export_selection(
        asset_name=asset_name,
        export_type=["obj", "abc"],
        _message=False
    )["obj"]
    instance = {}
    instance['name'] = asset_name
    instance['family'] = 'asset'
    instance['host'] = 'spp'
    instance['mesh_path'] = mesh_path

    update_spp(instance)


def right_click():
    pass


def double_click():
    pass

