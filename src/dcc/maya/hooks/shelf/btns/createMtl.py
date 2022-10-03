# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# MetaData
_annotation = "Quick create material and assign it on selection."
_icon = "shading.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""


# ---------------------------------
# import libraries
import os
import re
import sys
from pathlib import Path

# ---------------------------------
DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.maya.hooks.shelf.tool_settings import ExportSettings
from dcc.maya.api.cmds import Maya, maya_main_window
from dcc.maya.api.renderer import arnold

from maya import cmds

# Main function
def main():
    renderer = arnold
    ren_name = renderer.name
    ren_mtl = renderer.material_type

    ma_fn = Maya(renderer)

    result = cmds.promptDialog(
        title='{} ()'.format(ren_name.capitalize(), ren_mtl),
        message='Material Name',
        button=['Assign', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == 'Assign':
        txt = cmds.promptDialog(query=True, text=True)
    else:
        return

    mtl_name = re.findall(r'(?i)mtl', txt)
    if not mtl_name:
        txt = txt+"MTL"

    else:
        txt = re.sub(r'(?i)mtl', mtl_name[0].upper(), txt)

    ma_fn.assignMaterial(n=txt)



if __name__ == '__main__':
    main()