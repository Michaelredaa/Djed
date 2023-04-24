# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
from PySide2.QtWidgets import QMainWindow, QDesktopWidget
from PySide2.QtGui import QIcon
from PySide2.QtGui import QGuiApplication

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, ]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.dcc.maya.shelves.ui.template import Button

# ---------------------------------
# Variables
djed_order = 0.0
djed_annotation = ""
djed_icon = ""
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""


# ---------------------------------
# Start Here
class ExampleButton(Button):
    title = "Example"
    icon = "example.png"

    def generate_ui(self):
        pass

    def connect_events(self):
        pass

    def reset_ui(self):
        pass

    def apply(self):
        pass

    def help(self):
        pass


def left_click():
    btn = ExampleButton()
    btn.show()


def right_click():
    pass


def double_click():
    pass
