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

from djed import about
from djed.dcc.maya.api.cmds import maya_main_window

# ---------------------------------
# Variables
djed_order = 10.00
djed_annotation = "About"
djed_icon = "about.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""


# ---------------------------------
# Start Here


def left_click():
    about.message(maya_main_window())


def right_click():
    pass


def double_click():
    pass
