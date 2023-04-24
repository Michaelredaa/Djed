# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, ]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.dcc.maya.shelves.ui.template import Button
from djed.dcc.linker.to_blender import send_to_blender


# ---------------------------------
# Variables
djed_order = 5.00
djed_annotation = "Send selection to Blender"
djed_icon = "blender.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""


# ---------------------------------
# Start Here
class AddAsset(Button):
    title = "Open selection in Blender Setting"
    icon = "blender.png"

    asset_name = ""

    def generate_ui(self):
        gbox = QGridLayout(self)
        gbox.addItem(QSpacerItem(int(self.width() * 0.05), 20,
                                 QSizePolicy.MinimumExpanding,
                                 QSizePolicy.MinimumExpanding))

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


    def connect_events(self):
        pass


    def reset_ui(self):
        pass

    def apply(self):
        asset_name = self.ma.selection()[0]

        if self.cb_latest_published.isChecked():
            asset_name = self.ma.selection()[0]
            geo_paths = self.get_geometry(asset_name=asset_name, obj_file="", usd_geo_file="", abc_file="", fbx_file="")
            mesh_data = self.get_geometry(asset_name=asset_name, mesh_data='')['mesh_data']
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
                "asset_data": self.ma.get_asset_materials_data(asset_name)
            }

        data['name'] = asset_name
        data['family'] = 'asset'
        data['colorspace'] = 'aces'
        data['host'] = 'unreal'
        data['geometry_type'] = 'obj_file'

        send_to_blender(data)

    def help(self):
        pass


def left_click():
    btn = AddAsset()
    btn.apply()


def right_click():
    pass


def double_click():
    btn = AddAsset()
    btn.show()

