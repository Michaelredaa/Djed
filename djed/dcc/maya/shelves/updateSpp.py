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

sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('djed').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.maya.api.cmds import Maya
from dcc.linker.to_spp import update_spp


# Main function
def main():
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



if __name__ == '__main__':
    
    main()
    
