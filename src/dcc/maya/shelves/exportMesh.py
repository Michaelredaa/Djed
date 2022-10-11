# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# MetaData
_annotation = "Export selected geometry"
_icon = "exportMesh.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------
# import libraries

import os
import sys
from pathlib import Path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# ---------------------------------
DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.maya.shelves.tool_settings import ToolSettingsBase
from dcc.maya.api.cmds import maya_main_window

class ExportSettings(ToolSettingsBase):
    def __init__(self, parent=None):
        super(ExportSettings, self).__init__(parent, preset_name="export_preset")
        self.setupUi(self)

        self.set_title("Export Selection Setting")
        self.set_icon("exportMesh.png")

        self._init_ui()
        # self._connectEvents()
        self._startup()

    def startup(self):
        pass
        # self.onRecent()

    def get_presets(self):
        preset = {}
        preset["export_root"] = self.le_dir.text()
        preset["obj"] = self.cb_obj.isChecked()
        preset["fbx"] = self.cb_fbx.isChecked()
        preset["abc"] = self.cb_abc.isChecked()
        preset["usd"] = self.cb_usd.isChecked()
        return preset

    def set_presets(self, preset):
        self.le_dir.setText(preset["export_root"])
        self.cb_obj.setChecked(preset["obj"])
        self.cb_fbx.setChecked(preset["fbx"])
        self.cb_abc.setChecked(preset["abc"])
        self.cb_usd.setChecked(preset["usd"])

    def init_ui(self):

        gbox = QGridLayout(self)
        gbox.addWidget(QLabel(""), 0, 0, 1, 1, Qt.AlignRight)

        l_export = QLabel("Export Selected Geometry as: ")
        gbox.addWidget(l_export, 1, 0, 1, 1, Qt.AlignRight)
        gbox.addItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum), 1, 1)

        self.cb_obj = QCheckBox("obj")
        gbox.addWidget(self.cb_obj, 2, 1, 1, 1, Qt.AlignLeft)

        self.cb_fbx = QCheckBox("fbx")
        gbox.addWidget(self.cb_fbx, 3, 1, 1, 1, Qt.AlignLeft)

        self.cb_abc = QCheckBox("abc")
        gbox.addWidget(self.cb_abc, 4, 1, 1, 1, Qt.AlignLeft)

        self.cb_usd = QCheckBox("usd")
        gbox.addWidget(self.cb_usd, 5, 1, 1, 1, Qt.AlignLeft)

        self.vl_space.addLayout(gbox)
        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

    def connectEvents(self):
        self.pb_cancel.clicked.connect(lambda: self.close())
        # self.pb_browse.clicked.connect(self.onBrowse)
        # self.pb_apply.clicked.connect(self.onApply)
        # self.pb_save.clicked.connect(self.onSave)

        self.actionReset_Settings.triggered.connect(self.onRestSettings)
        self.actionSave_Settings.triggered.connect(self.onSaveSettings)
        self.le_dir.textChanged.connect(self.textChanges)

    def textChanges(self):
        if not self.toggle:
            self.switch_text = self.le_dir.text()

    def onApply(self):
        extensions = []
        if self.cb_obj.isChecked(): extensions.append("obj")
        if self.cb_fbx.isChecked(): extensions.append("fbx")
        if self.cb_abc.isChecked(): extensions.append("abc")
        if self.cb_usd.isChecked(): extensions.append("usd")

        export_path = self.le_dir.text()

        from dcc.maya.shelves.pyblish_launch import process
        process(path=export_path, extensions=extensions)
        # export_meshs = self.ma.export_selection(asset_dir=export_path, asset_name=None, export_type=extensions)

# Main function
def main():
    es = ExportSettings(parent=maya_main_window())
    if len(sys.argv) > 1:
        es.show()
    else:
        es.onApply()


if __name__ == '__main__':
    
    main()
    
