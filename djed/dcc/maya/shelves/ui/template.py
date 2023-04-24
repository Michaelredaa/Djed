# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
from PySide2.QtWidgets import QMainWindow
from PySide2.QtGui import QIcon
from PySide2.QtGui import QGuiApplication

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, ]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.dcc.maya.shelves.ui.tools_setting_ui import Ui_ToolSettings

from djed.dcc.maya.api.cmds import Maya, maya_main_window
from djed.utils.file_manager import FileManager
from djed.utils.assets_db import AssetsDB

from djed.utils.resources.style_rc import *

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
class Button(QMainWindow, Ui_ToolSettings):
    title = ""
    icon = ""
    Instance = []

    def __init__(self, parent=maya_main_window()):
        super(Button, self).__init__(parent)

        for ins in self.__class__.Instance:
            ins.close()
        self.__class__.Instance = [self]

        self.setupUi(self)

        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(f':/icons/{self.icon}'))

        self.fm = FileManager()
        self.ma = Maya()
        self.db = AssetsDB()

        self.generate_ui()
        self.save_settings()
        self._connect_events()

        # set size
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        screen_height = screen_geometry.height()
        self.setMinimumSize(screen_height * 0.3, screen_height * 0.1)

    def generate_ui(self):
        pass

    def _connect_events(self):
        self.pb_cancel.clicked.connect(lambda: self.close())
        self.pb_apply.clicked.connect(self.apply)
        self.pb_save.clicked.connect(self.save)

        self.actionReset_Settings.triggered.connect(self.reset_ui)
        self.actionHelp_on_this_tool.triggered.connect(self.help)

        self.connect_events()

    def connect_events(self):
        pass

    def reset_ui(self):
        pass

    def save_settings(self):
        pass

    def apply(self):
        pass

    def save(self):
        self.apply()
        self.close()
        self.deleteLater()

    def help(self):
        pass


def left_click():
    btn = Button()
    btn.show()


def right_click():
    pass


def double_click():
    pass


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
