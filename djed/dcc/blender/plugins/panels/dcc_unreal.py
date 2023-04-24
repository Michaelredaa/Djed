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
from djed.dcc.linker.to_unreal import send_to_unreal, is_unreal_connected
from djed.utils.assets_db import AssetsDB
from djed.utils.generic import validate_name

# ---------------------------------
# Variables
djed_order = 33
db = AssetsDB()


# ---------------------------------
# Start Here
class Unreal(bpy.types.Panel):
    """Creates an Unreal Djed Panel in the 3d window"""

    bl_label = "Unreal"
    bl_idname = "OBJECT_PT_djed_unreal"
    bl_description = "Djed Connections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        box = self.layout.box()
        row = box.row()
        row.alert = True
        row.operator("addonname.djed_send_unreal_operator")


class SendToUnreal(bpy.types.Operator):
    bl_label = "Send"
    bl_idname = "addonname.djed_send_unreal_operator"
    bl_description = "Send the selected geometry to Unreal"

    def draw(self, context):

        if not is_unreal_connected():
            self.report({'ERROR'}, 'Can not connect to Maya.\n'
                                   'Make sure you open Maya session or unreal command port is open.')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Sending to Maya')

        if len(selection()) < 1:
            self.report({'WARNING'}, 'Please make sure you select an object from outliner')
            return {'CANCELLED'}

        asset_name = validate_name(selection()[0].name)

        use_latest_published = context.scene.djed_use_latest_publish
        if not use_latest_published:
            result = export_geometry(
                asset_dir=None,
                asset_name=asset_name,
                export_type=["obj", "abc"]
            )
            if not result:
                return {'CANCELLED'}

        asset_data = db.get_geometry(asset_name=asset_name, mesh_data="")["mesh_data"]
        geo_paths = db.get_geometry(
            asset_name=asset_name,
            obj_file="",
            usd_geo_file="",
            abc_file="",
            fbx_file="",
            source_file="")

        colorspace = context.scene.djed_colorspace.lower()
        geometry_type = 'obj_file'
        renderer = 'standard'

        data = {
            'name': asset_name,
            'family': 'asset',
            'host': 'blender',
            'renderer': renderer,
            'colorspace': colorspace,
            'geometry_type': geometry_type,
            'geo_paths': geo_paths,
            'asset_data': asset_data,
        }
        send_to_unreal(data)

        return {'FINISHED'}


classes = [
    Unreal,
    SendToUnreal,

]


# Main Function
def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)



def unregister():
    for _cls in classes:
        bpy.utils.unregister_class(_cls)



