# -*- coding: utf-8 -*-
"""
Documentation:
"""


# ---------------------------------
# import libraries
import subprocess
import sys
import os
from pathlib import Path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
Icons = DJED_ROOT.joinpath('src', 'utils', 'resources', 'icons')


sysPaths = [str(DJED_ROOT), str(DJED_ROOT.joinpath('src'))]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

###########################
import importlib
import dcc.maya.api.cmds
importlib.reload(dcc.maya.api.cmds)

################################


from utils.file_manager import FileManager
from utils.assets_db import AssetsDB
from utils.dialogs import browse_dirs

from dcc.maya.api.cmds import Maya, maya_main_window

from dcc.maya.shelves.ui import (
    Ui_ToolSettings,
    Completer,
    ClickedLabel
)
maya_main_window()

db = AssetsDB()

SizeObject = QDesktopWidget().screenGeometry(-1)
ScreenHeight = SizeObject.height()
ScreenWidth = SizeObject.width()

Tokens = ["$selection", "$project"]


# ---------------------------------
class ToolSettingsBase(QMainWindow, Ui_ToolSettings):
    def __init__(self, parent=None, preset_name=None):
        super(ToolSettingsBase, self).__init__(parent)
        self.setupUi(self)

        self.presets_name = preset_name

        self.setMinimumSize(ScreenHeight * 0.3, ScreenHeight * 0.1)

        self.fm = FileManager()
        self.ma = Maya()

        self.maya_cfg = self.fm.get_cfg("maya")

        self.switch_text = None
        self.toggle = False

        self.setMinimumSize(ScreenHeight * 0.3, ScreenHeight * 0.1)

        # self._init_ui()
        # self._startup()

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(str(Icons.joinpath(icon))))

    def _startup(self):
        self._connectEvents()
        maya_user_cfg = self.fm.get_user_json("maya")
        if maya_user_cfg:
            preset = maya_user_cfg.get(self.presets_name)
            if not preset:
                preset = self.maya_cfg.get(self.presets_name)
        else:
            preset = self.maya_cfg.get(self.presets_name)
        self.set_presets(preset)
        self.startup()

    def startup(self):
        pass

    def set_presets(self, preset):
        pass

    def get_presets(self):
        return {}

    def _init_ui(self):
        # browse path
        self.l_exportDir = ClickedLabel("Export Directory: ")
        self.l_exportDir.leftClicked.connect(self.onDirClick)
        self.le_dir = QLineEdit()
        self.setCompleter(self.le_dir)
        self.pb_browse = QPushButton("")
        self.pb_browse.setIcon(QIcon(Icons.joinpath('folder.png').as_posix()))
        self.pb_browse.setIconSize(QSize(20, 20))
        self.pb_browse.setFlat(True)

        hbox_browse = QHBoxLayout(self)
        hbox_browse.addWidget(self.l_exportDir)
        hbox_browse.addWidget(self.le_dir)
        hbox_browse.addWidget(self.pb_browse)
        hbox_browse.setSpacing(5)
        self.vl_space.addLayout(hbox_browse)

        l = QLabel('Use tokens like $selection, $project,..\nClick on "Export Directory" to evaluate the directory')
        vbox_ = QHBoxLayout(self)
        vbox_.addItem(QSpacerItem(ScreenWidth * 0.07, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        vbox_.addWidget(l)
        self.vl_space.addLayout(vbox_)

        self.vl_space.addWidget(QLabel(""))
        self.init_ui()

    def init_ui(self):
        pass

    def _connectEvents(self):
        self.pb_cancel.clicked.connect(lambda: self.close())
        try:
            self.pb_browse.clicked.connect(self._onBrowse)
            self.le_dir.textChanged.connect(self.textChanges)
        except:
            pass
        self.pb_apply.clicked.connect(self._onApply)
        self.pb_save.clicked.connect(self._onSave)

        self.actionReset_Settings.triggered.connect(self._onRestSettings)
        self.actionSave_Settings.triggered.connect(self._onSaveSettings)

        self.connectEvents()

    def connectEvents(self):
        pass

    def _onSaveSettings(self):
        maya_user_cfg = self.fm.get_user_json("maya")
        maya_user_cfg[self.presets_name] = self.get_presets()
        self.fm.set_user_json(maya=maya_user_cfg)
        self.onSaveSettings()

    def onSaveSettings(self):
        pass

    def _onRestSettings(self):
        maya_user_cfg = self.fm.get_user_json("maya")
        presets = self.maya_cfg.get(self.presets_name)
        maya_user_cfg[self.presets_name] = presets
        self.set_presets(presets)
        self.fm.set_user_json(maya=maya_user_cfg)
        self.onRestSettings()

    def onRestSettings(self):
        pass

    def _onApply(self):
        self.onApply()

    def onApply(self):
        pass

    def _onSave(self):
        self.onSaveSettings()
        self.onApply()
        self.close()

    def onSave(self):
        pass

    def _onBrowse(self):

        le_text = self.le_dir.text()
        le_tex = self.convert_text_tokens(le_text)

        if not le_tex:
            le_tex = QDir.rootPath()
        self.fm.make_dirs(le_tex)

        new_dir = browse_dirs(self, "Select export directory", le_tex)
        if new_dir:
            self.le_dir.setText(new_dir)
        self.onBrowse()

    def onBrowse(self):
        pass

    def textChanges(self):
        if not self.toggle:
            self.switch_text = self.le_dir.text()

    def onDirClick(self):
        current_text = self.le_dir.text()

        self.toggle = not self.toggle
        if self.toggle:
            self.switch_text = current_text

        export_dir = self.convert_text_tokens(current_text)

        if not self.switch_text:
            return
        if self.toggle:
            self.le_dir.setText(export_dir)
            self.l_exportDir.setStyleSheet("background-color: rgba(0, 0, 0, 90)")
        else:
            self.l_exportDir.setStyleSheet("background-color: none")
            self.le_dir.setText(self.switch_text)

    def convert_text_tokens(self, text):

        tokens_text = text
        if self.ma.selection():
            tokens_text = text.replace("$selection", self.ma.selection()[0])
        if self.ma.get_project_dir():
            export_dir = tokens_text.replace("$project", self.ma.get_project_dir())

        export_root = self.ma.get_file_path()
        if not export_root:
            return
        for i in range(export_dir.count("../")):
            export_root = os.path.dirname(export_root)

        if "../" in export_dir:
            export_dir = os.path.join(export_root, export_dir.rsplit("../", 1)[-1]).replace("\\", "/")

        return export_dir

    def setCompleter(self, lineedit):
        # lineEdit completion
        completeModel = QStringListModel()
        completeModel.setStringList(Tokens)
        completer = Completer()
        completer.setModel(completeModel)
        lineedit.setCompleter(completer)



if __name__ == '__main__':
    print(__name__)
