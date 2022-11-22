# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# MetaData

_annotation = "Send selection to clarisse"
_icon = "sendClarisse.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------
# import libraries

import os
import sys
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
from utils.dialogs import message
from utils.generic import wait_until
from utils.sys_process import is_process_running
from utils.assets_db import AssetsDB
from utils.resources.style_rc import *
from dcc.linker.to_clarisse import send_to_clarisse
from dcc.clarisse.api.remote_connect import connect
from dcc.maya.api.renderer import arnold
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


class Maya2ClsSettings(ToolSettingsBase):
    def __init__(self, parent=None):
        super(Maya2ClsSettings, self).__init__(parent, preset_name="maya_clarisse")
        self.setupUi(self)

        self.set_title("Send Selection to Clarisse Settings")
        self.set_icon("sendClarisse.png")

        self.setMouseTracking(True)
        self.installEventFilter(self)

        self._init_ui()
        # self._connectEvents()
        self._startup()

    def _init_ui(self):
        # add ui
        # self.vl_space.addWidget(QLabel())

        gbox = QGridLayout(self)
        gbox.addItem(QSpacerItem(ScreenWidth * 0.05, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        # connection
        self.pb_connect = QPushButton()
        self.pb_connect.setFlat(True)
        self.pb_connect.setFixedSize(QSize(20, 20))
        ic = QIcon(":/icons/reload.png")
        self.pb_connect.setIcon(ic)
        self.pb_connect.setIconSize(QSize(20, 20))
        gbox.addWidget(self.pb_connect, 0, 4, 1, 1, Qt.AlignRight)

        gbox.addWidget(QLabel("Connection Status: "), 0, 5, 1, 1, Qt.AlignRight)
        self.connection = QLabel()
        self.connection.setFixedSize(QSize(10, 10))
        self.connection.setStyleSheet("border-radius: 5px; background: red;")
        gbox.addWidget(self.connection, 0, 6, 1, 1, Qt.AlignLeft)

        # open clarisse
        gbox.addWidget(QLabel("Open Empty: "), 1, 1, 1, 1, Qt.AlignRight)
        self.pb_cls = QPushButton()
        self.pb_cls.setFlat(True)
        self.pb_cls.setFixedSize(QSize(35, 35))
        ic = QIcon(":/icons/sendClarisse.png")
        self.pb_cls.setIcon(ic)
        self.pb_cls.setIconSize(QSize(35, 35))
        gbox.addWidget(self.pb_cls, 1, 2, 1, 1, Qt.AlignLeft)

        gbox.addWidget(QLabel(), 2, 1, 1, 1, Qt.AlignBottom)

        # port number
        gbox.addWidget(QLabel("Port Number: "), 3, 1, 1, 1, Qt.AlignRight)
        self.le_port_num = QLineEdit()
        reg_ex = QRegExp(r"^[0-9]+")
        input_validator = QRegExpValidator(reg_ex, self.le_port_num)
        self.le_port_num.setValidator(input_validator)
        self.le_port_num.setFixedSize(QSize(80, 20))
        gbox.addWidget(self.le_port_num, 3, 2, 1, 1, Qt.AlignLeft)

        # Geometry
        geos = ["Alembic Reference", "Alembic Bundle", "USD Reference", "USD Bundle"]
        gbox.addWidget(QLabel("Use Geometry as: "), 4, 1, 1, 1, Qt.AlignRight)
        self.com_geo = QComboBox()
        self.com_geo.setMinimumSize(QSize(170, 20))
        self.com_geo.addItems(geos)
        gbox.addWidget(self.com_geo, 4, 2, 1, 1, Qt.AlignLeft)

        gbox.addWidget(QLabel("Convert Materials: "), 5, 1, 1, 1, Qt.AlignRight)
        mats_from = ["arnold", ]
        mats_to = ["Autodesk Standard Surface", "Disney Principles"]
        gbox.addWidget(QLabel("From: "), 6, 1, 1, 1, Qt.AlignRight)
        self.com_mat_from = QComboBox()

        self.com_mat_from.addItems(mats_from)
        gbox.addWidget(self.com_mat_from, 6, 2, 1, 1, Qt.AlignLeft)
        self.com_mat_from.setFixedSize(QSize(170, 20))
        gbox.addWidget(QLabel("To: "), 7, 1, 1, 1, Qt.AlignRight)
        self.com_mat_to = QComboBox()
        self.com_mat_to.setFixedSize(QSize(170, 20))
        self.com_mat_to.addItems(mats_to)
        gbox.addWidget(self.com_mat_to, 7, 2, 1, 1, Qt.AlignLeft)

        # color space
        gbox.addWidget(QLabel("Convert Colorspace: "), 8, 1, 1, 1, Qt.AlignRight)
        hbox = QHBoxLayout()
        self.rb_aces = QRadioButton("Aces")
        self.rb_srgb = QRadioButton("sRGB")
        hbox.addWidget(self.rb_aces)
        hbox.addWidget(self.rb_srgb)
        gbox.addLayout(hbox, 8, 2, 1, 1)

        # Use published geometry
        gbox.addWidget(QLabel(""), 9, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(QLabel("Use published geometry: "), 10, 1, 1, 1, Qt.AlignRight)
        self.cb_latest_published = QCheckBox("")
        gbox.addWidget(self.cb_latest_published, 10, 2, 1, 1)

        self.vl_space.addLayout(gbox)
        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding))

    def connectEvents(self):
        self.pb_cls.clicked.connect(self.onClarisseOpen)
        self.pb_connect.clicked.connect(self.onConnect)

    def startup(self):
        self.port_connected = False

        self.onConnect()

    def onClarisseOpen(self):
        cls_exe = get_dcc_cfg('clarisse', 'configuration', 'executable')

        subprocess.Popen(f'"{cls_exe}" -flavor ifx')

        if wait_until(connect, 60):
            self.onConnect()

    def onConnect(self):
        if is_process_running("clarisse"):
            if not self.port_connected:
                port = connect()
                if port:
                    self.connection.setStyleSheet("border-radius: 5px; background: green;")
                    port.run('ix.log_info("Djed Tools Ready");ix.log_info("*"*100)')
                    self.port_connected = True
                else:
                    self.connection.setStyleSheet("border-radius: 5px; background: red;")
                    self.port_connected = False
        else:
            self.connection.setStyleSheet("border-radius: 5px; background: red;")
            self.port_connected = False

    def get_presets(self):
        preset = {}
        preset["command_port"] = int(self.le_port_num.text())
        preset["geometry_type"] = self.com_geo.currentText()
        preset["mtls_from"] = self.com_mat_from.currentText()
        preset["mtls_to"] = self.com_mat_to.currentText()
        preset["use_latest_publish"] = self.cb_latest_published.isChecked()
        if self.rb_aces.isChecked():
            preset["colorspace"] = "ACES"
        else:
            preset["colorspace"] = "sRGB"

        return preset

    def set_presets(self, preset):
        self.le_port_num.setText(str(preset["command_port"]))
        self.com_geo.setCurrentText(preset["geometry_type"])
        self.com_mat_from.setCurrentText(preset["mtls_from"])
        self.com_mat_to.setCurrentText(preset["mtls_to"])
        self.cb_latest_published.setChecked(preset["use_latest_publish"])

        if preset["colorspace"].lower() == "aces":
            self.rb_aces.setChecked(True)
        else:
            self.rb_srgb.setChecked(True)

    def onApply(self):
        geo_types = {
            "Alembic Reference": 'Alembic Reference',
            "USD Reference": 'USD Reference',
            "Alembic Bundle": 'Alembic Bundle',
            "USD Bundle": 'USD Bundle'
        }

        renderer_types = {
            "Autodesk Standard Surface": 'autodesk_standard_surface',
            "Disney Principles": 'disney'
        }

        if is_process_running("clarisse"):
            if not connect():
                message(self, "Error",
                        f'Make sure enable port at "{self.le_port_num.text()}"\n in clarisse: Edit>>Preferences under "Command Port" side tap.')
                return
        else:
            message(self, "Error", "Make sure you launch clarisse first")
            return

        port_num = int(self.le_port_num.text())
        geo_type = self.com_geo.currentText()
        mtl_from = self.com_mat_from.currentText()
        mtl_to = self.com_mat_to.currentText()
        if self.rb_aces.isChecked():
            colorspace = "aces"
        else:
            colorspace = "srgb"

        # publishing
        if self.cb_latest_published.isChecked():
            asset_name = ma.selection()[0]
            geo_paths = db.get_geometry(asset_name=asset_name, obj_file="", usd_geo_file="", abc_file="", fbx_file="",
                                        source_file="")
            data = {
                "name": asset_name,
                "family": "asset",
                "file_color_space": ma.get_file_colorspace(),
                "renderer": ma.get_renderer(),
                "host": "maya",
                "geo_paths": geo_paths,
                "asset_data": ma.get_asset_data(asset_name)
            }

        else:
            pyblish.api.register_host("maya")
            pyblish.api.register_plugin(CreateAsset)
            instance = pyblish.util.collect()[0]
            data = instance.data

        data['geometry_type'] = geo_types.get(geo_type)
        data['to_renderer'] = renderer_types.get(mtl_to)
        data['renderer'] = mtl_from
        data['colorspace'] = colorspace

        send_to_clarisse(data, port_num)

    def enterEvent(self, QEvent):
        self.onConnect()

    def leaveEvent(self, QEvent):
        # here teh code for mouse leave
        pass


# Main function
def main():
    m2c = Maya2ClsSettings(maya_main_window())
    if len(sys.argv) > 1:
        m2c.show()
    else:
        m2c.onApply()


if __name__ == '__main__':
    main()
