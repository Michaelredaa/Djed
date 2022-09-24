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

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
Icons = DJED_ROOT.joinpath('src', 'utils', 'resources', 'icons')


sysPaths = [str(DJED_ROOT), str(DJED_ROOT.joinpath('src'))]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)


from utils.file_manager import FileManager
from utils.assets_db import AssetsDB
from utils.dialogs import browse_dirs, message

from dcc.maya.api.cmds import Maya, maya_main_window
from dcc.clarisse.api.cmds import Clarisse
import dcc.linker.to_spp as spp

from dcc.maya.hooks.shelf.ui import (
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
class ToolSettings(QMainWindow, Ui_ToolSettings):
    def __init__(self, parent=None, preset_name=None):
        super(ToolSettings, self).__init__(parent)
        self.setupUi(self)

        self.presets_name = preset_name

        self.setMinimumSize(ScreenHeight * 0.3, ScreenHeight * 0.1)

        self.fm = FileManager()
        self.ma = Maya()

        self.maya_cfg = self.fm.get_cfg("maya")

        self.switch_text = None
        self.toggle = False

        self.setMinimumSize(ScreenHeight * 0.3, ScreenHeight * 0.1)

        # self._init_ui()
        # self._startup()

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(str(Icons.joinpath(icon))))

    def _startup(self):
        self._connectEvents()
        maya_user_cfg = self.fm.get_user_json("maya")
        if maya_user_cfg:
            preset = maya_user_cfg.get(self.presets_name)
            if not preset:
                preset = self.maya_cfg.get(self.presets_name)
        else:
            preset = self.maya_cfg.get(self.presets_name)
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
        self.pb_browse.setIcon(QIcon(Icons.joinpath('folder.png').as_posix()))
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
        maya_user_cfg = self.fm.get_user_json("maya")
        maya_user_cfg[self.presets_name] = self.get_presets()
        self.fm.set_user_json(maya=maya_user_cfg)
        self.onSaveSettings()

    def onSaveSettings(self):
        pass

    def _onRestSettings(self):
        maya_user_cfg = self.fm.get_user_json("maya")
        presets = self.maya_cfg.get(self.presets_name)
        maya_user_cfg[self.presets_name] = presets
        self.set_presets(presets)
        self.fm.set_user_json(maya=maya_user_cfg)
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


class ExportSettings(ToolSettings):
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
        export_meshs = self.ma.export_selection(asset_dir=export_path, asset_name=None, export_type=extensions)



class Maya2SppSettings(ToolSettings):
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
        instance = {}
        asset_name = self.ma.selection()[0]
        mesh_path = self.ma.export_selection(
            asset_dir=self.le_dir.text(),
            asset_name=asset_name,
            export_type=["obj", "abc"],
            _message=False
        )["obj"]

        instance['name'] = asset_name
        instance['data'] = {'mesh_path': mesh_path, 'cfg': cfg}

        spp.process(instance)



class Maya2ClsSettings(ToolSettings):
    def __init__(self, parent=None):
        super(Maya2ClsSettings, self).__init__(parent, preset_name="maya_clarisse_presets")
        self.setupUi(self)

        self.set_title("Send Selection to Clarisse Setting")
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
        ic = QIcon(os.path.join(Icons, "reload.png"))
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
        ic = QIcon(os.path.join(Icons, "sendClarisse.png"))
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
        geos = ["Alembic Reference", ]
        gbox.addWidget(QLabel("Use Geometry as: "), 4, 1, 1, 1, Qt.AlignRight)
        self.com_geo = QComboBox()
        self.com_geo.setMinimumSize(QSize(170, 20))
        self.com_geo.addItems(geos)
        gbox.addWidget(self.com_geo, 4, 2, 1, 1, Qt.AlignLeft)

        gbox.addWidget(QLabel("Convert Materials: "), 5, 1, 1, 1, Qt.AlignRight)
        mats_from = ["Arnold", ]
        mats_to = ["Autodesk Standard Surface"]
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

        self.vl_space.addLayout(gbox)
        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding))

    def connectEvents(self):
        self.pb_cls.clicked.connect(self.onClarisseOpen)
        self.pb_connect.clicked.connect(self.onConnect)

    def startup(self):
        self.port_connected = False
        self.cls = Clarisse()

        self.onConnect()

    def onClarisseOpen(self):
        cls_user_cfg = self.fm.get_user_json("clarisse")
        if cls_user_cfg:
            cls_exe = cls_user_cfg.get("clarisse_exe")
            if not cls_exe:
                cls_exe = self.fm.get_cfg("clarisse").get("clarisse_exe")
        else:
            cls_exe = self.fm.get_cfg("clarisse").get("clarisse_exe")

        subprocess.Popen(f'"{cls_exe}" -flavor ifx')

        if self.lk.wait_until(self.cls.connect, 60):
            self.onConnect()

    def onConnect(self):
        if self.lk.checkIfProcessRunning("clarisse"):
            if not self.port_connected:
                port = self.cls.connect()
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
        preset["port_num"] = int(self.le_port_num.text())
        preset["geo_type"] = self.com_geo.currentText()
        preset["mtls_from"] = self.com_mat_from.currentText()
        preset["mtls_to"] = self.com_mat_to.currentText()
        if self.rb_aces.isChecked():
            preset["colorspace"] = "aces"
        else:
            preset["colorspace"] = "srgb"

        return preset

    def set_presets(self, preset):
        self.le_port_num.setText(str(preset["port_num"]))
        self.com_geo.setCurrentText(preset["geo_type"])
        self.com_mat_from.setCurrentText(preset["mtls_from"])
        self.com_mat_to.setCurrentText(preset["mtls_to"])

        if preset["colorspace"] == "aces":
            self.rb_aces.setChecked(True)
        else:
            self.rb_srgb.setChecked(True)

    def onApply(self):
        if self.lk.checkIfProcessRunning("clarisse"):
            if not self.cls.connect():
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

        mtl_conversion = []
        if mtl_from == "Arnold":
            renderer = Arnold()
            mtl_conversion.append("aistd")
        else:
            return
        if mtl_to:
            mtl_conversion.append("adstd")
        else:
            return

        mayaData = self.ma.send_to_clarisse()
        asset_name = self.ma.selection()[0]
        if mayaData:
            clrs = Clarisse()
            clrs.set_port_num(port_num)
            try:
                clrs.connect()
            except:
                message(None, "Connection Failed",
                                "Connection Failed\n Make sure the clarisse is open and the command port open on '{}'".format(
                                    port_num))
                return

            cfg = {}
            cfg["colorspace"] = colorspace
            cfg["conversion"] = mtl_conversion
            cfg["geo_type"] = geo_type
            cfg["asset_name"] = asset_name

            clrs.maya_to_clarisse(mayaData, cfg=cfg)

    def enterEvent(self, QEvent):
        self.onConnect()

    def leaveEvent(self, QEvent):
        # here teh code for mouse leave
        pass


class CreateMtlTexs(ToolSettings):
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
        renderers = ["Arnold", ]
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
        rend_name = self.com_rend.currentText()
        tex_dir = self.convert_text_tokens(self.le_dir.text())

        if rend_name == "Arnold":
            renderer = Arnold()
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

        sp = SppMaya(renderer)
        sp.send_Maya(tex_dir, sgs=sgs, colorspace=colorspace)





if __name__ == '__main__':
    print(__name__)
