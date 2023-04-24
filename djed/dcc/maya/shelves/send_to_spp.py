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

# ---------------------------------
# Variables
djed_order = 2.00
djed_annotation = "Create material with imported textures from directory."
djed_icon = "sendSubstace.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""

# ---------------------------------
# Start Here


import djed.dcc.linker.to_spp
from importlib import reload

reload(djed.dcc.linker.to_spp)
##############################################


from djed.dcc.maya.shelves.ui.template import Button
from djed.dcc.maya.plugins import CreateAsset, CollectAssetData

from djed.dcc.linker.to_spp import send_to_spp
from djed.utils.resources.style_rc import *

import pyblish.api


class MayaSPP(Button):
    title = "Send Selection to Substance Painter Setting"
    icon = "sendSubstace.png"

    asset_name = ""

    def generate_ui(self):
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

        tiles = ["UVTile", "TextureSetPerUVTile"]
        self.com_tiles = QComboBox()
        self.com_tiles.addItems(tiles)
        gbox.addWidget(QLabel("Workflow Tiles: "), 3, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.com_tiles, 3, 2, 1, 1)

        self.cb_cam = QCheckBox("Import Camera")
        gbox.addWidget(QLabel(""), 4, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(self.cb_cam, 4, 2, 1, 1)

        self.vl_space.addLayout(gbox)

        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

    def connect_events(self):
        pass

    def reset_ui(self):
        self.com_res.setCurrentText('2048')
        self.com_normals.setCurrentText('OpenGl')
        self.rb_tangent_vertex.setChecked(True)
        self.com_tiles.setCurrentText('UVTile')
        self.cb_cam.setChecked(False)

    def save_settings(self, **kwargs):

        if kwargs:
            self.fm.set_user_json(maya={__name__: kwargs})
            return

        settings = self.fm.get_user_json('maya', __name__)

        if settings:
            self.com_res.setCurrentText(str(settings.get('default_texture_resolution')))
            self.com_normals.setCurrentText(settings.get('normal_map_format'))
            self.rb_tangent_vertex.setChecked(settings.get('tangent_space_mode') == 'PerVertex')
            self.rb_tangent_fragment.setChecked(not settings.get('tangent_space_mode') == 'PerVertex')
            self.com_tiles.setCurrentText(settings.get('project_workflow'))
            self.cb_cam.setChecked(settings.get('import_cameras'))

        else:
            self.reset_ui()

    def apply(self):

        cfg = self.get_cfg()

        class Update(pyblish.api.InstancePlugin):
            def process(self, instance):
                instance.data['hosts'] = 'spp'
                instance.data['cfg'] = cfg

        plugins = [CreateAsset, CollectAssetData, Update]

        pyblish.api.register_host("maya")
        for plugin in plugins:
            pyblish.api.register_plugin(plugin)

        # instance = pyblish.util.collect()[0]

        send_to_spp()

        self.save_settings(**cfg)

    def get_cfg(self):
        preset = {}
        preset["default_texture_resolution"] = int(self.com_res.currentText())
        preset["normal_map_format"] = self.com_normals.currentText()
        if self.rb_tangent_vertex.isChecked():
            preset["tangent_space_mode"] = "PerVertex"
        else:
            preset["tangent_space_mode"] = "PerFragment"

        preset["project_workflow"] = self.com_tiles.currentText()
        preset["import_cameras"] = self.cb_cam.isChecked()
        return preset

    def help(self):
        pass


def left_click():
    btn = MayaSPP()
    btn.apply()


def right_click():
    pass


def double_click():
    btn = MayaSPP()
    btn.show()
