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

from djed.dcc.maya.api.cmds import Maya
from djed.dcc.maya.api.renderer import arnold

from maya import cmds

# ---------------------------------
# Variables
djed_order = 1.20
djed_annotation = "Quick create material and assign it on selection."
djed_icon = "shading.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""

# ---------------------------------
# Start Here


def left_click():
    renderer = arnold
    ren_name = renderer.name
    ren_mtl = renderer.material_type

    ma = Maya(renderer)

    result = cmds.promptDialog(
        title='{} ({})'.format(ren_name.capitalize(), ren_mtl),
        message='Material Name',
        button=['Assign', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == 'Assign':
        txt = cmds.promptDialog(query=True, text=True)
    else:
        return
    txt = "".join([x.capitalize() for x in txt.split("_")])
    txt = txt[0].lower() + txt[1:]

    mtl_name = re.findall(r'(?i)mtl', txt)
    if not mtl_name:
        txt = txt+"MTL"

    else:
        txt = re.sub(r'(?i)mtl', mtl_name[0].upper(), txt)

    # remove underscore

    mtl, sg = ma.create_material(name=txt)
    ma.assign_material(objects=ma.selection(), sg_name=sg)



def right_click():
    pass


def double_click():
    pass

