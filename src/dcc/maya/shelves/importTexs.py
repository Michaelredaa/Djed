# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# MetaData

_annotation = "Create material with imported textures from directory."
_icon = "mtlTexture.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

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

#######################################
import importlib
import dcc.maya.plugins.load_asset
import dcc.maya.plugins.create_material_from_textures
importlib.reload(dcc.maya.plugins.load_asset)
importlib.reload(dcc.maya.plugins.create_material_from_textures)
#########################################



from dcc.maya.api import renderer
from dcc.maya.plugins import CreateMaterialFromTextures, LoadAsset
from dcc.maya.plugins.load_asset import LoadAsset
from dcc.maya.plugins.create_material_from_textures import CreateMaterialFromTextures

from dcc.maya.shelves.tool_settings import (
    ToolSettingsBase,
    ClickedLabel,
    Icons,
    ScreenWidth,
    maya_main_window
)

import pyblish.api
import pyblish.util

import maya.cmds as cmds


class CreateMtlTexs(ToolSettingsBase):
    def __init__(self, parent=None):
        super(CreateMtlTexs, self).__init__(parent, preset_name="create_mtl_tex_presets")
        self.setupUi(self)
        self.set_title("Create Material From Texture Setting")
        self.set_icon("mtlTexture.png")

        self._init_ui()
        self._startup()

    def _init_ui(self):
        # add ui
        # browse path
        self.l_exportDir = ClickedLabel("Texture Directory: ")
        self.l_exportDir.leftClicked.connect(self.onDirClick)
        self.le_dir = QLineEdit()
        self.setCompleter(self.le_dir)
        self.pb_browse = QPushButton("")
        self.pb_browse.setIcon(QIcon(os.path.join(Icons, "folder.png")))
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

        gbox = QGridLayout(self)

        # renderers
        renderers = ["arnold", ]
        gbox.addWidget(QLabel("Renderer: "), 0, 1, 1, 1, Qt.AlignRight)
        self.com_rend = QComboBox()
        self.com_rend.setMinimumSize(QSize(150, 20))
        self.com_rend.addItems(renderers)
        gbox.addWidget(self.com_rend, 0, 2, 1, 1, Qt.AlignLeft)

        # udims
        gbox.addWidget(QLabel("Use UDIM Workflow: "), 1, 1, 1, 1, Qt.AlignRight)
        self.cb_udim = QCheckBox()
        gbox.addWidget(self.cb_udim, 1, 2, 1, 1, Qt.AlignLeft)

        l_naming = QLabel("$mesh_$materialName_$mapType.<UIDM>.ext")
        l_naming_h = QLabel("Naming Conventional: ")
        gbox.addWidget(l_naming_h, 2, 1, 1, 1, Qt.AlignRight)
        gbox.addWidget(l_naming, 2, 2, 1, 1, Qt.AlignLeft)
        l_naming.setStyleSheet("color: gray")
        l_naming_h.setStyleSheet("color: gray")

        # materials
        gbox.addWidget(QLabel("Materials to Creates: "), 3, 1, 1, 1, Qt.AlignRight)
        self.com_mtls = QComboBox()
        self.com_mtls.setMinimumSize(QSize(150, 20))
        gbox.addWidget(self.com_mtls, 3, 2, 1, 1, Qt.AlignLeft)

        # color space
        gbox.addWidget(QLabel("Convert Colorspace: "), 8, 1, 1, 1, Qt.AlignRight)
        hbox = QHBoxLayout()
        self.rb_aces = QRadioButton("Aces")
        self.rb_srgb = QRadioButton("sRGB")
        hbox.addWidget(self.rb_aces)
        hbox.addWidget(self.rb_srgb)
        gbox.addLayout(hbox, 8, 2, 1, 1)

        self.vl_space.addLayout(gbox)
        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding))

    def connectEvents(self):
        self.cb_udim.toggled.connect(self.onChangeUdim)

    def startup(self):
        self.onChangeUdim()

    def get_presets(self):
        preset = {}
        preset["tex_dir"] = self.le_dir.text()
        preset["renderer"] = self.com_rend.currentText()
        preset["mtls"] = "All"
        preset["udim"] = self.cb_udim.isChecked()
        if self.rb_aces.isChecked():
            preset["colorspace"] = "aces"
        else:
            preset["colorspace"] = "srgb"

        return preset

    def set_presets(self, preset):
        self.le_dir.setText(preset["tex_dir"])
        self.com_rend.setCurrentText(preset["renderer"])
        self.com_mtls.setCurrentText(preset["mtls"])
        self.cb_udim.setChecked(preset["udim"])
        self.cb_udim.setDisabled(True)

        if preset["colorspace"] == "aces":
            self.rb_aces.setChecked(True)
        else:
            self.rb_srgb.setChecked(True)

    def onBrowse(self):
        self.onChangeUdim()

    def onChangeUdim(self):
        self.com_mtls.clear()
        tex_dir = self.convert_text_tokens(self.le_dir.text())
        if not tex_dir:
            return

        if not os.path.isdir(tex_dir):
            os.makedirs(tex_dir)

        sgs = self.fm.get_sgName_from_textures(tex_dir)
        sgs.insert(0, "All")
        self.com_mtls.addItems(sgs)

    def onApply(self):
        renderer_name = self.com_rend.currentText()
        tex_dir = self.convert_text_tokens(self.le_dir.text())

        if renderer_name == "arnold":
            active_renderer = renderer.arnold
        else:
            return

        sgs_selection = self.com_mtls.currentText()

        if sgs_selection == "All":
            sgs = None
        else:
            sgs = [sgs_selection]

        if self.rb_aces.isChecked():
            colorspace = "aces"
        else:
            colorspace = "srgb"


        context = pyblish.api.Context()
        instance_obj = CreateMaterialFromTextures(tex_dir)
        instance = instance_obj.process(context)
        LoadAsset().process(instance)


# Main function
def main():
    cm = CreateMtlTexs(maya_main_window())
    if len(sys.argv) > 1:
        cm.show()
    else:
        current_path = cm.convert_text_tokens(cm.le_dir.text())

        tex_dir = cmds.fileDialog2(dir=current_path, ds=2, fm=3, okc="select")
        if tex_dir:
            cm.le_dir.setText(tex_dir[0])
            cm.onApply()


if __name__ == '__main__':
    main()
