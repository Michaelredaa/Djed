# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# MetaData
_annotation = "Send selection to substance painter"
_icon = "sendSubstace.png"
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
from dcc.linker.to_spp import to_spp


class Maya2SppSettings(ToolSettingsBase):
    def __init__(self, parent=None):
        super(Maya2SppSettings, self).__init__(parent, preset_name="maya_spp_presets")
        self.setupUi(self)

        self.set_title("Open selection in Substance Painter Setting")
        self.set_icon("sendSubstace.png")

        self._init_ui()
        self._connectEvents()
        self._startup()

    def init_ui(self):
        # add ui
        gbox = QGridLayout(self)
        gbox.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum), 0, 0)

        res = ["512", "1024", "2048", "4096"]
        self.com_res = QComboBox()
        self.com_res.addItems(res)
        gbox.addWidget(QLabel("Resolution: "), 0, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.com_res, 0, 2, 1, 1)

        normls = ["OpenGL", "DirectX"]
        self.com_normals = QComboBox()
        self.com_normals.addItems(normls)
        gbox.addWidget(QLabel("Normals Map: "), 1, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.com_normals, 1, 2, 1, 1)

        self.rb_tangent_vertex = QRadioButton("Per Vertex")
        self.rb_tangent_fragment = QRadioButton("Per Fragment")
        gbox.addWidget(QLabel("Compute Tangents: "), 2, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.rb_tangent_vertex, 2, 2, 1, 1)
        gbox.addWidget(self.rb_tangent_fragment, 2, 3, 1, 1)
        gbox.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum), 2, 4)

        tiles = ["UVTile"]
        self.com_tiles = QComboBox()
        self.com_tiles.addItems(tiles)
        gbox.addWidget(QLabel("Workflow Tiles: "), 3, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.com_tiles, 3, 2, 1, 1)

        self.cb_cam = QCheckBox("Import Camera")
        gbox.addWidget(QLabel(""), 4, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.cb_cam, 4, 2, 1, 1)

        self.vl_space.addLayout(gbox)

        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

    def get_presets(self):
        preset = {}
        preset["export_root"] = self.le_dir.text()
        preset["default_texture_resolution"] = int(self.com_res.currentText())
        preset["normal_map_format"] = self.com_normals.currentText()
        if self.rb_tangent_vertex.isChecked():
            preset["tangent_space_mode"] = "PerVertex"
        else:
            preset["tangent_space_mode"] = "PerFragment"

        preset["project_workflow"] = self.com_tiles.currentText()
        preset["import_cameras"] = self.cb_cam.isChecked()
        return preset

    def set_presets(self, preset):
        self.le_dir.setText(preset["export_root"])
        self.com_res.setCurrentText(str(preset["default_texture_resolution"]))
        self.com_normals.setCurrentText(preset["normal_map_format"])
        self.rb_tangent_vertex.setChecked(preset["tangent_space_mode"] == "PerVertex")
        self.rb_tangent_fragment.setChecked(preset["tangent_space_mode"] == "PerFragment")
        self.com_normals.setCurrentText(preset["project_workflow"])
        self.cb_cam.setChecked(preset["import_cameras"])

    def onApply(self):
        cfg = self.get_presets()
        data = {}
        asset_name = self.ma.selection()[0]
        mesh_path = self.ma.export_selection(
            asset_dir=self.le_dir.text(),
            asset_name=asset_name,
            export_type=["obj", "abc"],
            _message=False
        )["obj"]

        data['name'] = asset_name
        data['family'] = 'asset'
        data['host'] = 'spp'
        data['mesh_path'] = mesh_path
        data['cfg'] = cfg

        to_spp(data)


# Main function
def main():
    m2s = Maya2SppSettings(maya_main_window())
    if len(sys.argv) > 1:
        m2s.show()
    else:
        m2s.onApply()




if __name__ == '__main__':
    main()

