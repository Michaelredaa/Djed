# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
import site
from pathlib import Path



DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

site.addsitedir(DJED_ROOT.joinpath('venv/python/Lib/site-packages').as_posix())

import pyblish.api
import pyblish.util

from djed.dcc.maya.api.cmds import Maya, maya_main_window
from djed.utils.assets_db import AssetsDB
from djed.utils.dialogs import message
from djed.settings.settings import get_asset_root, get_dcc_cfg
from djed.utils.logger import Logger
from djed.utils.file_manager import PathResolver

import maya.cmds as cmds

# ---------------------------------
# Variables
db = AssetsDB()


# ---------------------------------
# Start Here
class CreateAsset(pyblish.api.ContextPlugin):
    label = "Get current asset info"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    families = ["asset"]

    def process(self, context):
        ma = Maya()
        self.log = Logger(
            name='maya-createAsset',
            use_file=get_dcc_cfg('general', 'settings', 'enable_logger')
        )

        self.log.debug("Create maya asset..")

        selection = ma.selection(fullpath=True)

        if len(selection) != 1 or '.' in selection[0]:
            message(maya_main_window(), "Warring", "You should select the asset main group only.")
            raise

        asset_name = selection[0].split('|')[-1]

        if not ma.is_group(selection[0]):
            message(maya_main_window(), "Warring", "You should select the asset main group only.")
            raise

        asset_uuid = ma.add_str_attribute(selection[0], 'djedId')
        if isinstance(asset_uuid, bool):
            asset_uuid = db.add_asset(asset_name=asset_name, gallery=0)
            ma.set_str_attribute(selection[0], 'djedId', asset_uuid)
            self.log.debug(f"Add asset to db on {asset_uuid}")

        # Add attributes
        ma.add_attr_to_shapes(objects=selection, attr_name="materialBinding")

        asset_root = get_asset_root(asset_name=asset_name)
        export_root = get_dcc_cfg('general', 'path', 'publish', 'model')
        self.log.debug(f"Work on root:  `{export_root}`")

        export_root = PathResolver(export_root)
        export_root.format(asset_root=asset_root, asset_name=asset_name)

        # version
        padding = get_dcc_cfg("general", "settings", "version_padding")
        geo_version = db.get_versions(uuid=asset_uuid, table_name='geometry')
        if geo_version:
            version = geo_version[0]["version"] + 1
        else:
            version = 1

        version = 'v' + f'{version}'.zfill(int(padding))
        export_root.format(version=version)
        self.log.debug(f"Work on version:  `{version}`")

        export_root = str(export_root).rsplit('.', 1)[0]

        if not os.path.isdir(os.path.dirname(export_root)):
            os.makedirs(os.path.dirname(export_root))

        # export geos
        geo_paths = {}
        obj_file = export_root+'.obj'
        ma.export_geo(node_name=selection[0], geo_path=obj_file)
        geo_paths['obj_file'] = obj_file

        abc_file = export_root + '.abc'
        ma.export_geo(
            node_name=selection[0],
            geo_path=abc_file,
            attrs='materialBinding'
        )
        geo_paths['abc_file'] = export_root + '.abc'

        usd_file = export_root + '.usdc'
        ma.export_geo(node_name=selection[0], geo_path=usd_file)
        geo_paths['usd_file'] = usd_file

        # update database
        db.add_geometry(uuid=asset_uuid, obj_file=obj_file, abc_file=abc_file)
        db.add_usd(uuid=asset_uuid, geo_file=usd_file)

        # materials
        materials = ma.get_asset_materials_data(selection[0])
        db.add_material(uuid=asset_uuid, geo_file=usd_file)

        instance = context.create_instance(
            name=asset_name,
            selection=selection,
            uuid=asset_uuid,
            family="asset",
            file_color_space=ma.get_file_colorspace(),
            renderer=ma.get_renderer(),
            material=materials,
            host="maya",
            geo_paths=geo_paths
        )


# Main Function
def main():
    pyblish.api.register_host("maya")
    pyblish.api.register_plugin(CreateAsset)

    instance = pyblish.util.collect()[0]
    print(instance)
    # pyblish.util.publish()


if __name__ == '__main__':
    main()
