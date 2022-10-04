# -*- coding: utf-8 -*-
"""
Documentation:
"""
import importlib
import os
import sys
import traceback
from pathlib import Path

from PySide2.QtWidgets import *
from PySide2.QtGui import *

import substance_painter as sp

# ---------------------------------
# Variables
DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT, DJED_ROOT.joinpath('src')]
for sysPath in sysPaths:
    if str(sysPath) not in sys.path:
        sys.path.append(str(sysPath))

from utils.dialogs import save_dialog, text_dialog, message
from utils.assets_db import AssetsDB
from utils.file_manager import FileManager
from dcc.spp.api import pipeline

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
        self.project_dir = ""
        self.exported_textures = dict()

        self.init_menus()

    def __del__(self):
        sp.ui.delete_ui_element(self.menu)

    def init_menus(self):

        self.asset_name = db.get_latest_edit_asset_name()
        asset_action = self.menu.addAction(self.asset_name)
        self.menu.addSeparator()

        save_action = self.menu.addAction(QIcon(str(Icons.joinpath('save.png'))), "&Save")
        save_incremental_action = self.menu.addAction(QIcon(str(Icons.joinpath('increment.png'))), "&Save incremental")
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
        save_incremental_action.triggered.connect(self.on_save_incremental)
        save_backup_action.triggered.connect(self.on_save_backup)
        open_action.triggered.connect(self.on_open_location)
        export_action.triggered.connect(self.on_textures_export)
        maya_action.triggered.connect(self.on_send_to_maya)
        clarisse_action.triggered.connect(self.on_send_to_clarisse)
        export_texture_action.triggered.connect(self.on_export_settings)

        about_action.triggered.connect(self.on_about)

    def on_save(self):
        save_path = self.get_save_path()
        if not save_path:
            spp_path = save_dialog(self.main_window, "Files (*.spp)")
            if not spp_path:
                return
        else:
            spp_path = save_path + ".spp"

        spp_path = self.fm.version_file_up(spp_path)

        pipeline.save_file(str(spp_path))

        db.add_geometry(asset_name=self.asset_name, substance_file=spp_path)

    def on_save_incremental(self):
        save_path = self.get_save_path()
        if not save_path:
            spp_path = save_dialog(self.main_window, "Files (*.spp)")
            if not spp_path:
                return
        else:
            spp_path = save_path + ".spp"

        spp_path = self.fm.version_file_up(spp_path)

        pipeline.save_incremental(spp_path)
        db.add_geometry(asset_name=self.asset_name, substance_file=spp_path)

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
        pipeline.export_texture()
        # add texture to db

    def on_export_settings(self):
        options = self.fm.get_user_json("spp", "export_preset")
        options["path"] = os.path.dirname(self.get_export_texture_path())

        if not options["preset"].endswith(".spexp"):
            options["preset"] = sp.resource.ResourceID(context="allegorithmic", name=options["preset"]).url()

        x = self.js.open_export_window(**options)

        return

    def on_send_to_maya(self):
        pass

    def on_send_to_clarisse(self):
        pass

    def on_about(self):
        pass

    def get_save_path(self):
        source_file_path = db.get_geometry(asset_name=self.asset_name, source_file="")["source_file"]
        if not (source_file_path and os.path.isfile(source_file_path)):
            message(self.main_window, "Error",
                    f"'{source_file_path}' is not an path\nIt seems you not save the source maya file.")
            return

        save_root = self.fm.get_user_json("spp", "save_dir")

        resolved_path = self.fm.resolve_path(
            save_root,
            relatives_to=source_file_path,
            variables={"$asset_name": self.asset_name, "$project": self.project_dir})

        return self.fm.version_file_up(resolved_path)

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
            resolved_path = self.fm.version_up(resolved_path)

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
