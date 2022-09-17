# -*- coding: utf-8 -*-
"""
Documentation:
"""


# ---------------------------------
# import libraries
import os
import sys
import importlib

# ---------------------------------
DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
resources = os.path.join(DJED_ROOT, "Scripts", "Utils", "Resources")
dcc = os.path.join(scripts, "dcc")
dcc_maya = os.path.join(dcc, "Maya")

sysPathes = [DJED_ROOT, scripts, dcc, dcc_maya, resources]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)


import ToolSettings
importlib.reload(ToolSettings)
from Maya_Functions import maya_main_window


def export_selection():
    es = ToolSettings.ExportSettings()
    es.onApply()

def export_selection_options():
    es = ToolSettings.ExportSettings(maya_main_window())
    es.show()



# Main function
def main():

    if len(sys.argv)>1:
        export_selection_options()
    else:
        export_selection()


if __name__ == '__main__':
    main()
