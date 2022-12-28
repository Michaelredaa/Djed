# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# MetaData

_annotation = "Send selection to unreal"
_icon = "unreal.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------
# import libraries

import os
import sys
import json
from pathlib import Path
import subprocess

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# ---------------------------------
DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from settings.settings import get_dcc_cfg
from utils.assets_db import AssetsDB
from utils.resources.style_rc import *
from dcc.linker.to_unreal import send_to_unreal

from dcc.maya.plugins.create_asset import CreateAsset
from dcc.maya.api.cmds import maya_main_window, Maya

import pyblish.api
import pyblish.util

from dcc.maya.shelves.tool_settings import (
    ToolSettingsBase,
    ScreenWidth,
)

db = AssetsDB()
ma = Maya()


class Maya2UnrealSettings(ToolSettingsBase):
    def __init__(self, parent=None):
        super(Maya2UnrealSettings, self).__init__(parent, preset_name="maya_unreal")
        self.setupUi(self)

        self.set_title("Open selection in unreal Setting")
        self.set_icon("unreal.png")

        self._init_ui()
        self._startup()

    def _init_ui(self):
        # add ui
        gbox = QGridLayout(self)
        gbox.addItem(QSpacerItem(ScreenWidth * 0.05, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        l = QLabel()
        l.setFixedSize(QSize(120, 20))
        gbox.addWidget(l, 0, 4, 1, 1, Qt.AlignRight)

        geo_types = []
        self.com_geo_types = QComboBox()
        self.com_geo_types.addItems(geo_types)
        gbox.addWidget(QLabel("Geometry Types: "), 0, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.com_geo_types, 0, 2, 1, 1)

        self.cb_latest_published = QCheckBox("Use latest published geometry")
        gbox.addWidget(QLabel(""), 1, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.cb_latest_published, 1, 2, 1, 1)

        self.vl_space.addLayout(gbox)

        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

    def get_presets(self):
        preset = {}
        preset["geometry_type"] = int(self.com_geo_types.currentText())
        preset["use_latest_publish"] = self.cb_latest_published.isChecked()
        return preset

    def set_presets(self, preset):
        self.com_geo_types.setCurrentText(str(preset["geometry_type"]))
        self.cb_latest_published.setChecked(preset["use_latest_publish"])

    def onApply(self):

        data = {}
        asset_name = self.ma.selection()[0]

        if self.cb_latest_published.isChecked():
            asset_name = ma.selection()[0]
            geo_paths = db.get_geometry(asset_name=asset_name, obj_file="", usd_geo_file="", abc_file="", fbx_file="")
            mesh_data = json.loads(db.get_geometry(asset_name=asset_name, mesh_data='')['mesh_data'])
            data = {
                "geo_paths": geo_paths,
                "asset_data": mesh_data
            }
        else:
            mesh_path = self.ma.export_selection(
                asset_name=asset_name,
                export_type=["obj", "abc"],
                _message=False
            )["obj"]

            data = {
                "geo_paths": {'obj_file': mesh_path},
                "asset_data": ma.get_asset_data(asset_name)
            }

        data['name'] = asset_name
        data['family'] = 'asset'
        data['colorspace'] = 'aces'
        data['host'] = 'unreal'
        data['geometry_type'] = 'obj_file'

        send_to_unreal(data)


# Main function
def main():
    m2c = Maya2UnrealSettings(maya_main_window())
    if len(sys.argv) > 1:
        m2c.show()
    else:
        m2c.onApply()


if __name__ == '__main__':
    main()
