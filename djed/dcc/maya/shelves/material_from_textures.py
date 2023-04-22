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
djed_order = 1.30
djed_annotation = "Create material with imported textures from directory."
djed_icon = "mtlTexture.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""

Tokens = ["{work_dir}", "{asset_name}", "{version}"]

# ---------------------------------
# Start Here


from djed.dcc.maya.shelves.ui.template import Button
from djed.dcc.maya.api import renderer
from djed.dcc.maya.plugins.load_asset import LoadAsset
from djed.dcc.maya.plugins.create_material_from_textures import CreateMaterialFromTextures
from djed.utils.textures import get_sgName_from_textures
from djed.settings.settings import get_asset_root, get_dcc_cfg
from djed.utils.dialogs import browse_dirs
from djed.utils.file_manager import PathResolver
from djed.utils.resources.style_rc import *

from djed.dcc.maya.shelves.ui import (
    Completer,
    ClickedLabel,
)

import pyblish.api
import pyblish.util

import maya.cmds as cmds


class MaterialTextures(Button):
    title = "Create Material From Texture Setting"
    icon = "mtlTexture.png"

    asset_name = ""
    toggle = False

    def generate_ui(self):

        # browse path
        self.l_exportDir = ClickedLabel("Texture Directory: ")
        self.l_exportDir.leftClicked.connect(self.on_dir_clicked)
        self.le_dir = QLineEdit()

        self.set_completer(self.le_dir)
        self.pb_browse = QPushButton("")
        self.pb_browse.setIcon(QIcon(":/icons/folder.png"))
        self.pb_browse.setIconSize(QSize(20, 20))
        self.pb_browse.setFlat(True)

        hbox_browse = QHBoxLayout(self)
        hbox_browse.addWidget(self.l_exportDir)
        hbox_browse.addWidget(self.le_dir)
        hbox_browse.addWidget(self.pb_browse)
        hbox_browse.setSpacing(5)
        self.vl_space.addLayout(hbox_browse)

        l = QLabel('Use tokens like {asset_root}, {asset_name}, ..\n'
                   'Click on "Export Directory" to evaluate the directory')
        vbox_ = QHBoxLayout(self)
        vbox_.addItem(QSpacerItem(int(self.width() * 0.17), 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        vbox_.addWidget(l)
        self.vl_space.addLayout(vbox_)

        self.vl_space.addWidget(QLabel(""))

        gbox = QGridLayout(self)

        # renderers
        renderers = [self.ma.get_renderer(), ]
        gbox.addWidget(QLabel("Renderer: "), 0, 0, 1, 1, Qt.AlignRight)
        self.com_rend = QComboBox()
        self.com_rend.setMinimumSize(QSize(150, 20))
        self.com_rend.addItems(renderers)
        gbox.addWidget(self.com_rend, 0, 1, 1, 1, Qt.AlignLeft)

        # udims
        gbox.addWidget(QLabel("Use UDIM Workflow: "), 1, 0, 1, 1, Qt.AlignRight)
        self.cb_udim = QCheckBox()
        gbox.addWidget(self.cb_udim, 1, 1, 1, 1, Qt.AlignLeft)

        l_naming = QLabel("{mesh}_{materialName}_{mapType}.{udim}.{ext}")
        l_naming_h = QLabel("Naming Conventional: ")
        gbox.addWidget(l_naming_h, 2, 0, 1, 1, Qt.AlignRight)
        gbox.addWidget(l_naming, 2, 1, 1, 1, Qt.AlignLeft)
        l_naming.setStyleSheet("color: gray")
        l_naming_h.setStyleSheet("color: gray")

        # materials
        gbox.addWidget(QLabel("Materials to Creates: "), 3, 0, 1, 1, Qt.AlignRight)
        self.com_mtls = QComboBox()
        self.com_mtls.setMinimumSize(QSize(150, 20))
        gbox.addWidget(self.com_mtls, 3, 1, 1, 1, Qt.AlignLeft)

        # color space
        gbox.addWidget(QLabel("Colorspace: "), 8, 0, 1, 1, Qt.AlignRight)
        hbox = QHBoxLayout()
        self.rb_aces = QRadioButton("Aces")
        self.rb_srgb = QRadioButton("sRGB")
        hbox.addWidget(self.rb_aces)
        hbox.addWidget(self.rb_srgb)
        gbox.addLayout(hbox, 8, 1, 1, 1)

        self.vl_space.addLayout(gbox)
        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding))

        self.on_change_udim()


    def connect_events(self):
        self.cb_udim.toggled.connect(self.on_change_udim)
        self.le_dir.editingFinished.connect(self.on_change_udim)
        self.pb_browse.clicked.connect(self.on_change_udim)
        self.pb_browse.clicked.connect(self.on_browse)

    def on_browse(self):
        le_text = self.le_dir.text()
        le_tex = self.convert_text_tokens(le_text)

        if not le_tex:
            le_tex = QDir.rootPath()
        self.fm.make_dirs(le_tex)

        new_dir = browse_dirs(self, "Select export directory", le_tex)
        if new_dir:
            self.le_dir.setText(new_dir)

    def on_dir_clicked(self):
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

    def on_change_udim(self):
        self.com_mtls.clear()
        tex_dir = self.convert_text_tokens(self.le_dir.text())
        if not tex_dir:
            return

        if not os.path.isdir(tex_dir):
            os.makedirs(tex_dir)

        sgs = get_sgName_from_textures(tex_dir)
        sgs.insert(0, "All")
        self.com_mtls.addItems(sgs)

    def set_completer(self, lineedit):
        # lineEdit completion
        completeModel = QStringListModel()
        completeModel.setStringList(Tokens)
        completer = Completer()
        completer.setModel(completeModel)
        lineedit.setCompleter(completer)

    def convert_text_tokens(self, text):

        path_resolver = PathResolver(text)
        asset_name = self.ma.selection()

        if asset_name:
            asset_name = asset_name[0]
        else:
            asset_name = ''

        path_resolver.format(
            asset_root=get_asset_root(asset_name),
            asset_name=asset_name,
        )

        # get latest version
        if '{version}' in str(path_resolver):
            root = str(path_resolver).split('{version}')[0]
            if not os.path.isdir(root):
                return str(path_resolver)

            version = self.fm.get_latest_folder_version(
                root,
                prefix='v',
                padding=int(get_dcc_cfg("general", "settings", "version_padding")),
                ret_path=False
            )

            path_resolver.format(version=version)

        return str(path_resolver)

    def reset_ui(self):

        published_textures = get_dcc_cfg('general', 'path', 'publish', 'textures')
        textures_root = os.path.dirname(published_textures)

        self.le_dir.setText(textures_root)
        self.com_rend.setCurrentText('arnold')
        self.cb_udim.setChecked(False)
        self.com_mtls.setCurrentText('All')
        self.rb_aces.setChecked(True)

    def save_settings(self, **kwargs):

        if kwargs:
            self.fm.set_user_json(maya={__name__: kwargs})
            return

        settings = self.fm.get_user_json('maya', __name__)

        if settings:
            self.le_dir.setText(settings.get('textures_dir'))
            self.com_rend.setCurrentText(settings.get('renderer'))
            self.cb_udim.setChecked(settings.get('udim'))
            self.rb_aces.setChecked(settings.get('aces'))
            self.rb_srgb.setChecked(not settings.get('aces'))
        else:
            self.reset_ui()



    def apply(self):
        renderer_name = self.com_rend.currentText()
        tex_dir = self.convert_text_tokens(self.le_dir.text())

        if renderer_name.lower() == "arnold":
            active_renderer = renderer.arnold
        else:
            return

        udim = self.cb_udim.isChecked()

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
        instance.data['colorspace'] = colorspace
        instance.data['execute_materials'] = sgs
        LoadAsset().process(instance)

        self.save_settings(textures_dir=self.le_dir.text(), renderer=renderer_name, udim=udim, aces=colorspace == 'aces')


    def help(self):
        pass


def left_click():
    btn = MaterialTextures()
    current_path = btn.convert_text_tokens(btn.le_dir.text())

    tex_dir = cmds.fileDialog2(dir=current_path, ds=2, fm=3, okc="select")
    if tex_dir:
        btn.le_dir.setText(tex_dir[0])
        btn.onApply()


def right_click():
    pass


def double_click():
    btn = MaterialTextures()
    btn.show()
