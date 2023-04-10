# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
import json
from pathlib import Path

import bpy

DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.dcc.blender.api.pipeline import selection, export_geometry
from djed.dcc.linker.to_spp import send_to_spp, update_spp
from djed.utils.assets_db import AssetsDB
from utils.generic import validate_name

# ---------------------------------
# Variables
djed_order = 31
db = AssetsDB()


# ---------------------------------
# Start Here
class SPP(bpy.types.Panel):
    """Creates a Substance Painter Djed Panel in the 3d window"""

    bl_label = "Substance Painter"
    bl_idname = "OBJECT_PT_djed_spp"
    bl_description = "Djed Connections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        box = self.layout.box()
        row = box.row()
        row.alert = True
        row.operator("addonname.djed_send_spp_operator")
        row.operator("addonname.djed_update_spp_operator")


class SendToSPP(bpy.types.Operator):
    bl_label = "Send"
    bl_idname = "addonname.djed_send_spp_operator"
    bl_description = "Send the selected geometry to Substance Painter"

    def execute(self, context):
        self.report({'INFO'}, 'Sending to Substance Painter')
        cfg = {}  # TODO Add custom configurations

        use_latest_published = context.scene.djed_use_latest_publish

        if len(selection()) < 1:
            self.report({'CANCELLED'}, 'Please make sure you select an object from outliner')
            return {'FINISHED'}

        asset_name = validate_name(selection()[0].name)

        if not use_latest_published:
            result = export_geometry(
                asset_dir=None,
                asset_name=asset_name,
                export_type=["obj", "abc"]
            )
            if not result:
                return {'CANCELLED'}

        geo_paths = db.get_geometry(
            asset_name=asset_name,
            obj_file="",
            usd_geo_file="",
            abc_file="",
            fbx_file="",
            source_file="")


        data = {
            'name': asset_name,
            'family': 'asset',
            'host': 'spp',
            'mesh_path': geo_paths['obj_file'],
            'cfg': cfg,
        }

        send_to_spp(data)
        return {'FINISHED'}



class UpdateToSPP(bpy.types.Operator):
    bl_label = "Update"
    bl_idname = "addonname.djed_update_spp_operator"
    bl_description = "Update the selected geometry to Substance Painter"

    def execute(self, context):
        self.report({'INFO'}, 'Updating Substance Painter')
        cfg = {}  # TODO Add custom configurations

        if len(selection()) < 1:
            self.report({'WARNING'}, 'Please make sure you select an object from outliner')
            return {'CANCELLED'}

        asset_name = validate_name(selection()[0].name)

        mesh_paths = export_geometry(
            asset_dir=None,
            asset_name=asset_name,
            export_type=["obj", "abc"]
        )

        data = {
            'name': asset_name,
            'family': 'asset',
            'host': 'spp',
            'mesh_path': mesh_paths['obj'],
            'cfg': cfg,
        }

        update_spp(data)

        return {'FINISHED'}


classes = [
    SPP,
    SendToSPP, UpdateToSPP,

]


# Main Function
def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def unregister():
    for _cls in classes:
        bpy.utils.unregister_class(_cls)


# Main Function
def main():
    register()


if __name__ == '__main__':
    main()
