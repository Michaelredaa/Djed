# -*- coding: utf-8 -*-
"""
Documentation:
"""
import importlib
import json
import os
import sys
import traceback
from pathlib import Path

from PySide2.QtWidgets import *
from PySide2.QtGui import *

import substance_painter as sp
import substance_painter_plugins

# ---------------------------------
# Variables

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT, DJED_ROOT.joinpath('src')]
for sysPath in sysPaths:
    if str(sysPath) not in sys.path:
        sys.path.append(str(sysPath))

##################################
import importlib
import utils.file_manager
from dcc.spp.api import pipeline
import dcc.linker.to_maya

importlib.reload(utils.file_manager)
importlib.reload(pipeline)
importlib.reload(dcc.linker.to_maya)
##################################



from utils.dialogs import save_dialog, text_dialog, message
from utils.assets_db import AssetsDB
from utils.file_manager import FileManager
from utils.generic import merge_dicts
from dcc.spp.api import pipeline
from dcc.linker.to_maya import send_to_maya
from dcc.linker.to_clarisse import send_to_clarisse

Icons = DJED_ROOT.joinpath("src", "utils", "resources", "icons")

INTEGRATION_PLUGIN = None

db = AssetsDB()


class SubstanceIntegration():
    def __init__(self):
        self.fm = FileManager()
        self.js = pipeline.JS()

        self.menu = QMenu("DJED")
        self.main_window = pipeline.main_window()

        self.asset_name = ''
        self.project_dir = ''
        self.exported_textures = dict()

        self.init_menus()

    def __del__(self):
        sp.ui.delete_ui_element(self.menu)

    def init_menus(self):

        self.asset_name = db.get_latest_edit_asset_name()
        asset_action = self.menu.addAction(self.asset_name)
        self.menu.addSeparator()

        save_action = self.menu.addAction(QIcon(str(Icons.joinpath('save.png'))), "&Save")
        # save_incremental_action = self.menu.addAction(QIcon(str(Icons.joinpath('increment.png'))), "&Save incremental")
        save_backup_action = self.menu.addAction(QIcon(str(Icons.joinpath('backup.png'))), "&Save Backup")
        open_action = self.menu.addAction(QIcon(str(Icons.joinpath('folder.png'))), "&Open Location")
        self.menu.addSeparator()
        export_action = self.menu.addAction(QIcon(str(Icons.joinpath('export.png'))), "&Fast Export")
        self.menu.addSeparator()
        maya_action = self.menu.addAction(QIcon(str(Icons.joinpath('maya.png'))), "&To Maya")
        clarisse_action = self.menu.addAction(QIcon(str(Icons.joinpath('settings.png'))), "&To Clarisse")

        self.menu.addSeparator()
        settings_menu = self.menu.addMenu(QIcon(str(Icons.joinpath('settings.png'))), "&Settings")
        export_texture_action = settings_menu.addAction("&Texture Export")
        self.menu.addSeparator()
        about_action = self.menu.addAction(QIcon(str(Icons.joinpath('about.png'))), "&About")

        sp.ui.add_menu(self.menu)

        # signals
        save_action.triggered.connect(self.on_save)
        # save_incremental_action.triggered.connect(self.on_save_incremental)
        save_backup_action.triggered.connect(self.on_save_backup)
        open_action.triggered.connect(self.on_open_location)
        export_action.triggered.connect(self.on_textures_export)
        maya_action.triggered.connect(self.on_send_to_maya)
        clarisse_action.triggered.connect(self.on_send_to_clarisse)
        export_texture_action.triggered.connect(self.on_export_settings)

        about_action.triggered.connect(self.on_about)

    def on_save(self):

        if not sp.project.is_open():
            message(self.main_window, 'Error', 'Please open project first.')
            return

        save_path = self.get_save_path()
        save_path = self.fm.version_file_up(save_path)
        if not save_path:
            spp_path = save_dialog(self.main_window, "Files (*.spp)")
            if not spp_path:
                return

        pipeline.save_incremental(str(save_path))

        db.add_geometry(asset_name=self.asset_name, substance_file=save_path)

    def on_save_backup(self):
        comment = text_dialog(self.main_window)

        file_path = Path(pipeline.get_file_path())
        file_dir = file_path.parent

        backup_dir = file_dir.joinpath('backup')
        backup_dir.mkdir(parents=True, exist_ok=True)

        pipeline.save_copy(f'{backup_dir.joinpath(file_path.stem)}_{comment}.spp')

    def on_open_location(self):
        self.fm.open_in_expoler(pipeline.get_file_path())

    def on_textures_export(self):

        # get presets
        presets = self.fm.get_user_json("spp", "export_preset")
        self.js.set_export_preset_name(presets["preset"])

        # export textures
        tex_data, version = pipeline.export_texture(tex_dir=os.path.dirname(presets["path"]))

        # update database
        old_data = db.get_geometry(asset_name=self.asset_name, mesh_data="")["mesh_data"]
        old_data = json.loads(old_data)

        new_data = dict(merge_dicts(old_data, tex_data))

        db.add_geometry(asset_name=self.asset_name, mesh_data=json.dumps(new_data))
        # add texture to db

    def on_export_settings(self):
        options = self.fm.get_user_json("spp", "export_preset")
        options["path"] = os.path.dirname(self.get_export_texture_path())

        if (not options["preset"].endswith(".spexp")) and options["preset"].startswith('resource://'):
            options["preset"] = sp.resource.ResourceID(context="allegorithmic", name=options["preset"]).url()

        # open window
        x = self.js.open_export_window(**options)

        # save presets
        new_preset = self.js.get_export_preset_name()
        if new_preset.endswith(".spexp"):
            new_preset = pipeline.get_preset_name_from_url(new_preset)

        new_presets = {
            'path': self.js.get_export_path()+'/$version',
            'preset': new_preset,
            'format': self.js.get_current_export_option()['fileFormat']
        }
        self.fm.set_user_json(spp={"export_preset": new_presets})

        return

    def on_send_to_maya(self):
        self.on_textures_export()

        asset_data = db.get_geometry(asset_name=self.asset_name, mesh_data="")["mesh_data"]
        asset_data = json.loads(asset_data)
        data = {
            'name': self.asset_name,
            'host': 'spp',
            'to_renderer': 'arnold',
            'source_renderer': 'standard',
            'asset_data': asset_data,
        }
        send_to_maya(data)

    def on_send_to_clarisse(self):
        self.on_textures_export()

        asset_data = db.get_geometry(asset_name=self.asset_name, mesh_data="")["mesh_data"]
        asset_data = json.loads(asset_data)
        geo_paths = db.get_geometry(asset_name=self.asset_name, obj_file="", usd_geo_file="", abc_file="", fbx_file="",
                                    source_file="")

        data = {
            'name': self.asset_name,
            'host': 'spp',
            'renderer': 'arnold',
            'to_renderer': 'standardSurface',
            'source_renderer': 'standard',
            'colorspace': 'aces',
            'geo_type': 'abc_bundle',
            'geo_paths': geo_paths,
            'asset_data': asset_data,
        }
        send_to_clarisse(data)

    def on_about(self):

        sys.path.append(DJED_ROOT.joinpath("src", "dcc", "spp", "hooks", "plugins").as_posix())
        plugin = importlib.import_module("Djed")
        substance_painter_plugins.reload_plugin(plugin)

    def get_save_path(self):
        source_file_path = db.get_geometry(asset_name=self.asset_name, source_file="")["source_file"]
        if not (source_file_path and os.path.isfile(source_file_path)):
            message(self.main_window, "Error",
                    f"'{source_file_path}' is not an path\nIt seems you not save the source maya file.")
            return

        save_root = self.fm.get_user_json("spp", "save_dir")

        resolved_dir = self.fm.resolve_path(
            save_root,
            relatives_to=source_file_path,
            variables={"$asset_name": self.asset_name, "$project": self.project_dir})
        resolved_path = os.path.join(resolved_dir, self.asset_name + "_sur_v0000.spp")
        return resolved_path

    def get_export_texture_path(self):
        source_file_path = db.get_geometry(asset_name=self.asset_name, source_file="")["source_file"]
        if not (source_file_path and os.path.isfile(source_file_path)):
            message(self.main_window, "Error",
                    f"'{source_file_path}' is not an path\nIt seems you not save the source maya file.")
            return

        export_root = self.fm.get_user_json("spp", "export_preset").get("path")

        resolved_path = self.fm.resolve_path(
            export_root,
            relatives_to=source_file_path,
            variables={"$asset_name": self.asset_name, "$project": self.project_dir})

        if "$version" in resolved_path:
            resolved_path = resolved_path.replace("$version", "")
            resolved_path, version = self.fm.version_up(resolved_path)

        save_path = str(resolved_path).replace("\\", "/")

        return save_path


def start_plugin():
    try:
        global INTEGRATION_PLUGIN
        INTEGRATION_PLUGIN = SubstanceIntegration()
    except:
        print(traceback.format_exc())


def close_plugin():
    global INTEGRATION_PLUGIN
    del INTEGRATION_PLUGIN


# Main function
def main():
    sp = SubstanceIntegration()
    # sp.onToMaya()
    # start_plugin()


if __name__ == '__main__':
    main()
