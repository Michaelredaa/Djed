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


from settings.settings import get_dcc_cfg, set_value
from utils.dialogs import save_dialog, text_dialog, message
from utils.assets_db import AssetsDB
from utils.file_manager import FileManager
from utils.generic import merge_dicts
from utils.resources.style_rc import *
from utils.resources.stylesheet import get_stylesheet
from dcc.spp.api import pipeline
from dcc.linker.to_maya import send_to_maya, is_maya_connected
from dcc.linker.to_clarisse import send_to_clarisse, is_clarisse_connected
import about


INTEGRATION_PLUGIN = None

db = AssetsDB()


class SubstanceIntegration():
    def __init__(self):
        self.fm = FileManager()
        self.js = pipeline.JS()

        self.menu = QMenu("DJED")
        self.menu.setStyleSheet(get_stylesheet())
        self.main_window = pipeline.main_window()

        self.asset_name = ''
        self.project_dir = self.fm.get_user_json('general', 'project')
        if self.project_dir is None:
            self.project_dir = ''
        self.exported_textures = dict()

        self.init_menus()

    def __del__(self):
        sp.ui.delete_ui_element(self.menu)

    def init_menus(self):

        self.asset_name = db.get_latest_edit_asset_name()
        asset_action = self.menu.addAction(self.asset_name)
        self.menu.addSeparator()

        save_action = self.menu.addAction(QIcon(':/icons/save.png'), "&Save")
        # save_incremental_action = self.menu.addAction(QIcon(str(Icons.joinpath('increment.png'))), "&Save incremental")
        save_backup_action = self.menu.addAction(QIcon(':/icons/backup.png'), "&Save Backup")
        open_action = self.menu.addAction(QIcon(':/icons/folder.png'), "&Open Location")
        self.menu.addSeparator()
        export_action = self.menu.addAction(QIcon(':/icons/export.png'), "&Export Textures")
        self.menu.addSeparator()
        maya_action = self.menu.addAction(QIcon(':/icons/maya.png'), "&To Maya")
        unreal_action = self.menu.addAction(QIcon(':/icons/unreal.png'), "&To Unreal")
        clarisse_action = self.menu.addAction(QIcon(':/icons/clarisse.png'), "&To Clarisse")

        self.menu.addSeparator()
        settings_menu = self.menu.addMenu(QIcon(':/icons/settings.png'), "&Settings")
        export_texture_action = settings_menu.addAction("&Texture Export")
        # latest textures
        self.use_latest_textures_action = settings_menu.addAction("&Use Latest Textures on DCC")
        self.use_latest_textures_action.setCheckable(True)
        try:
            latest_texture_status = get_dcc_cfg("substance_painter", "configuration", 'use_latest_textures')
        except:
            latest_texture_status = True
        self.use_latest_textures_action.setChecked(latest_texture_status)
        self.menu.addSeparator()

        # recent
        self.recent_menu = self.menu.addMenu("&Recent")
        self.populate_recent_files()

        about_action = self.menu.addAction(QIcon(':/icons/about.png'), "&About")

        sp.ui.add_menu(self.menu)

        # signals
        save_action.triggered.connect(self.on_save)
        # save_incremental_action.triggered.connect(self.on_save_incremental)
        save_backup_action.triggered.connect(self.on_save_backup)
        open_action.triggered.connect(self.on_open_location)
        export_action.triggered.connect(self.on_textures_export)
        maya_action.triggered.connect(self.on_send_to_maya)
        unreal_action.triggered.connect(self.on_send_to_unreal)
        clarisse_action.triggered.connect(self.on_send_to_clarisse)
        export_texture_action.triggered.connect(self.on_export_settings)
        self.recent_menu.triggered.connect(self.on_recent_clicked)

        about_action.triggered.connect(self.on_about)

        # reload the plugin
        # reload_action = self.menu.addAction("&Reload")
        # reload_action.triggered.connect(self._on_reload_plugin())

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

        # add to recent
        self.add_to_recent(save_path)

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
        presets = get_dcc_cfg("substance_painter", "texture_export")
        self.js.set_export_preset_name(presets["preset"])

        # export textures
        tex_dir = presets["path"]
        tex_dir = self.fm.resolve_path(
            tex_dir,
            relatives_to=pipeline.get_file_path(),
        )
        tex_data, version = pipeline.export_texture(tex_dir=tex_dir)

        # update database
        old_data = db.get_geometry(asset_name=self.asset_name, mesh_data="")["mesh_data"]
        old_data = json.loads(old_data)

        new_data = dict(merge_dicts(old_data, tex_data))

        db.add_geometry(asset_name=self.asset_name, mesh_data=json.dumps(new_data))
        # add texture to db

    def on_export_settings(self):
        options = get_dcc_cfg("substance_painter", "texture_export")
        options["path"] = self.get_export_texture_path()

        if (not options["preset"].endswith(".spexp")) and options["preset"].startswith('resource://'):
            options["preset"] = sp.resource.ResourceID(context="allegorithmic", name=options["preset"]).url()

        # open window
        x = self.js.open_export_window(**options)

        # save presets
        new_preset = self.js.get_export_preset_name()
        if new_preset.endswith(".spexp"):
            new_preset = pipeline.get_preset_name_from_url(new_preset)

        new_presets = {
            'path': self.js.get_export_path() + '/$version',
            'preset': new_preset,
            'format': self.js.get_current_export_option()['fileFormat']
        }

        for key, value in new_preset.items():
            set_value(value, "substance_painter", "texture_export", key)

        return

    def on_send_to_maya(self):

        if is_maya_connected():
            if not self.use_latest_textures_action.isChecked():
                self.on_textures_export()

            settings = get_dcc_cfg("substance_painter", "plugins", 'substance_painter_maya')

            asset_data = db.get_geometry(
                asset_name=self.asset_name,
                obj_file="",
                usd_geo_file="",
                abc_file="",
                fbx_file="",
                source_file="",
                mesh_data=""
            )

            import_type = settings.get('geometry_type')

            data = {
                'name': self.asset_name,
                'host': 'spp',
                'to_renderer': settings.get('use_material'),
                'source_renderer': 'standard',
                'colorspace': settings.get('colorspace').lower(),
                'geometry_type': 'abc_file',
                'import_type': import_type,
                'geo_paths': asset_data,
                'asset_data': json.loads(asset_data.get('mesh_data')),
            }
            send_to_maya(data)
        else:
            message(self.main_window, "Error",
                    "Can not connect to maya.\nMake sure you open maya or maya command port is open.")

    def on_send_to_clarisse(self):
        if is_clarisse_connected():
            if not self.use_latest_textures_action.isChecked():
                self.on_textures_export()

            settings = get_dcc_cfg("substance_painter", "plugins", 'substance_painter_clarisse')
            to_render = settings.get('use_material')
            to_render = '_'.join(to_render.lower().split(' '))

            asset_data = db.get_geometry(asset_name=self.asset_name, mesh_data="")["mesh_data"]
            asset_data = json.loads(asset_data)
            geo_paths = db.get_geometry(
                asset_name=self.asset_name,
                obj_file="",
                usd_geo_file="",
                abc_file="",
                fbx_file="",
                source_file="")

            data = {
                'name': self.asset_name,
                'host': 'spp',
                'renderer': 'arnold',
                'to_renderer': to_render,
                'source_renderer': 'standard',
                'colorspace': settings.get('colorspace').lower(),
                'geometry_type': settings.get('geometry_type'),
                'geo_paths': geo_paths,
                'asset_data': asset_data,
            }
            send_to_clarisse(data)
            print(data)
        else:
            message(self.main_window, "Error",
                    "Can not connect to clarisse.\nMake sure you open clarisse session or clarisse command port is open.")

    def on_send_to_unreal(self):
        from dcc.linker.to_unreal import send_to_unreal

        if not self.use_latest_textures_action.isChecked():
            self.on_textures_export()

        # settings = get_dcc_cfg("substance_painter", "plugins", 'substance_painter_clarisse')

        asset_data = db.get_geometry(asset_name=self.asset_name, mesh_data="")["mesh_data"]
        asset_data = json.loads(asset_data)
        geo_paths = db.get_geometry(
            asset_name=self.asset_name,
            obj_file="",
            usd_geo_file="",
            abc_file="",
            fbx_file="",
            source_file="")

        data = {
            'name': self.asset_name,
            'host': 'unreal',
            'renderer': 'arnold',
            'colorspace': 'aces',
            'geometry_type': 'obj_file',
            'geo_paths': geo_paths,
            'asset_data': asset_data,
        }
        send_to_unreal(data)

    def on_about(self):
        about.message(self.main_window)

    def _on_reload_plugin(self):
        plugin = importlib.import_module("Djed")
        substance_painter_plugins.reload_plugin(plugin)

    def get_save_path(self):
        source_file_path = db.get_geometry(asset_name=self.asset_name, source_file="")["source_file"]
        if not (source_file_path and os.path.isfile(source_file_path)):
            message(self.main_window, "Error",
                    f"'{source_file_path}' is not an path\nIt seems you not save the source maya file.")
            return

        save_root = get_dcc_cfg("substance_painter", "configuration", "spp_save_directory")
        print({"$asset_name": self.asset_name, "$project": self.project_dir})
        resolved_dir = self.fm.resolve_path(
            save_root,
            relatives_to=source_file_path,
            variables={"$asset_name": self.asset_name, "$project": self.project_dir})
        resolved_path = os.path.join(resolved_dir, self.asset_name + "_sur_v0000.spp")
        return resolved_path

    def get_export_texture_path(self):
        export_root = get_dcc_cfg("substance_painter", "texture_export").get("path")

        resolved_path = self.fm.resolve_path(
            export_root,
            relatives_to=pipeline.get_file_path(),
            variables={"$asset_name": self.asset_name, "$project": self.project_dir})

        if "$version" in resolved_path:
            resolved_path = resolved_path.replace("$version", "")
            resolved_path, version = self.fm.version_folder_up(resolved_path)

        save_path = str(resolved_path).replace("\\", "/")

        return save_path

    def add_to_recent(self, filepath):
        recent_list = self.fm.get_user_json('spp', 'recent')
        if not recent_list:
            self.fm.set_user_json(spp={'recent': []})

        recent_list = self.fm.get_user_json('spp', 'recent')
        recent_list.append(filepath)
        if len(recent_list) > 10:
            recent_list = recent_list[len(recent_list) - 10:]
        self.fm.set_user_json(spp={'recent': recent_list})

        self.populate_recent_files()

    def populate_recent_files(self):
        [self.recent_menu.removeAction(x) for x in self.recent_menu.findChildren(QAction)]
        recent_list = self.fm.get_user_json('spp', 'recent')
        if not recent_list:
            return

        for item_path in reversed(recent_list):
            recent_action = self.recent_menu.addAction(item_path)

    def on_recent_clicked(self, action):
        path = action.text()
        pipeline.open_file(path)


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
