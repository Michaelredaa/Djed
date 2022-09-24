# -*- coding: utf-8 -*-
"""
Documentation: 
"""
# ---------------------------------
# MetaData
_annotation = "Update selection to substance painter current session"
_icon = "updateSubstance.png"
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

from dcc.maya.api.cmds import Maya
from dcc.linker import update_spp


# Main function
def main():
    ma_fn = Maya()
    mesh_path = ma_fn.export_selection(export_type=["obj", "abc"], message=False)["obj"]
    instance = {'name': '', 'data': {'mesh_path': mesh_path}}

    update_spp.process(instance)


if __name__ == '__main__':
    
    main()
    
