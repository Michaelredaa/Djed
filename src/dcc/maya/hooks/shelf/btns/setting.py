# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# import libraries
import sys
import maya.cmds as cmds

# ---------------------------------
# MetaData
_annotation = "Send selection to substance painter"
_icon = "settings.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------

from src.version import version

# Main function
def main():
    cmds.confirmDialog( title='Djed Tools', message=version)


if __name__ == '__main__':

    main()
    
