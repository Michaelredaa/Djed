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

from settings.settings import get_dcc_cfg

DJED_ROOT = Path(os.getenv("DJED_ROOT"))

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
from utils.resources.style_rc import *
from settings.settings import get_value, set_value, reset_value
from dcc.maya.api.cmds import Maya

from dcc.maya.shelves.ui import (
    Ui_ToolSettings,
    Completer,
    ClickedLabel
)

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

        self.switch_text = None
        self.toggle = False

        self.setMinimumSize(ScreenHeight * 0.3, ScreenHeight * 0.1)

        # self._init_ui()
        # self._startup()

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(f':/icons/{icon}'))

    def get_cfg(self):
        maya_plugins_cfg = get_value('plugins', 'maya', 'plugins').get('children', [])
        current_preset_list = [x.get('children') for x in maya_plugins_cfg if x.get('name') == self.presets_name][0]
        preset = {x.get('name'): x.get('value') for x in current_preset_list}
        return preset

    def _startup(self):
        self._connectEvents()

        preset = self.get_cfg()
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
        self.pb_browse.setIcon(QIcon(':/icons/folder.png'))
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
        for key, value in self.get_presets().items():
            set_value(value, 'maya', 'plugins', self.presets_name, key)

        self.onSaveSettings()

    def onSaveSettings(self):
        pass

    def _onRestSettings(self):
        preset = self.get_cfg()
        for key, value in preset.items():
            set_value(value, 'maya', 'plugins', self.presets_name, key)
            reset_value(key, "maya", "plugins", self.presets_name, key)

        preset = self.get_cfg()
        self.set_presets(preset)
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
