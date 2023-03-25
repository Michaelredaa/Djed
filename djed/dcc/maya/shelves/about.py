# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# import libraries
import sys
import os
from pathlib import Path
import maya.cmds as cmds


# ---------------------------------
# MetaData
_annotation = "About"
_icon = "about.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------
DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('djed').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed import about
from dcc.maya.api.cmds import maya_main_window

# Main function
def main():
    about.message(maya_main_window())


if __name__ == '__main__':
    main()
