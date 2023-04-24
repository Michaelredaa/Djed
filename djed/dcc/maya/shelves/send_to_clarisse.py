# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
import subprocess

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, ]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

# ---------------------------------
# Variables
djed_order = 3.00
djed_annotation = "Send selection to clarisse"
djed_icon = "sendClarisse.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""


# ---------------------------------
# Start Here

from djed.dcc.maya.shelves.ui.template import Button
from djed.settings.settings import get_dcc_cfg
from djed.utils.dialogs import message
from djed.utils.generic import wait_until
from djed.utils.sys_process import is_process_running
from djed.dcc.linker.to_clarisse import send_to_clarisse
from djed.dcc.clarisse.api.remote_connect import connect
from djed.dcc.maya.plugins.create_asset import CreateAsset
from djed.utils.resources.style_rc import *


import pyblish.api
import pyblish.util
class MayaClarisse(Button):
    title = "Send Selection to Clarisse Settings"
    icon = "sendClarisse.png"

    asset_name = ""

    def generate_ui(self):

        self.setMouseTracking(True)
        self.installEventFilter(self)

        # add ui
        # self.vl_space.addWidget(QLabel())

        gbox = QGridLayout(self)
        gbox.addItem(QSpacerItem(
            int(self.width() * 0.05), 20,
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding))

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

    def connect_events(self):
        self.pb_cls.clicked.connect(self.on_clarisse_open)
        self.pb_connect.clicked.connect(self.on_connect)


    def on_clarisse_open(self):
        cls_exe = get_dcc_cfg('clarisse', 'configuration', 'executable')

        subprocess.Popen(f'"{cls_exe}" -flavor ifx')

        if wait_until(connect, 60):
            self.onConnect()
    def on_connect(self):
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

    def reset_ui(self):
        pass
    def apply(self):
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
            asset_name = self.ma.selection()[0]
            geo_paths = self.db.get_geometry(asset_name=asset_name, obj_file="", usd_geo_file="", abc_file="", fbx_file="",
                                        source_file="")
            data = {
                "name": asset_name,
                "family": "asset",
                "file_color_space": self.ma.get_file_colorspace(),
                "renderer": self.ma.get_renderer(),
                "host": "maya",
                "geo_paths": geo_paths,
                "asset_data": self.ma.get_asset_materials_data(asset_name)
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
        self.on_connect()

    def leaveEvent(self, QEvent):
        # here teh code for mouse leave
        pass

    def help(self):
        pass


def left_click():
    btn = MayaClarisse()
    btn.apply()


def right_click():
    pass


def double_click():
    btn = MayaClarisse()
    btn.show()

