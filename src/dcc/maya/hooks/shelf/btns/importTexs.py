# -*- coding: utf-8 -*-
"""
Documentation: 
"""


# ---------------------------------
# MetaData
_annotation = "Create material with imported textures from directory."
_icon = "mtlTexture.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""



# import libraries

import os
import sys
from pathlib import Path

# ---------------------------------
DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.maya.hooks.shelf.tool_settings import CreateMtlTexs
from dcc.maya.api.cmds import maya_main_window

import maya.cmds as cmds

# Main function
def main():

    cm = CreateMtlTexs(maya_main_window())
    if len(sys.argv) > 1:
        cm.show()
    else:
        current_path = cm.convert_text_tokens(cm.le_dir.text())

        tex_dir = cmds.fileDialog2(dir=current_path, ds=2,fm=3, okc="select")
        if tex_dir:
            cm.le_dir.setText(tex_dir[0])
            cm.onApply()




if __name__ == '__main__':
    main()
