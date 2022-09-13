# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# MetaData
_annotation = "Send selection to substance painter"
_icon = "sendSubstace.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------
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

from dcc.maya.hooks.shelf.tool_settings import Maya2SppSettings
from dcc.maya.api.cmds import maya_main_window


# Main function
def main():
    m2s = Maya2SppSettings(maya_main_window())
    if len(sys.argv) > 1:
        m2s.show()
    else:
        m2s.onApply()




if __name__ == '__main__':
    main()

