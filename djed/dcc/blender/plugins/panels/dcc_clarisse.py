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
from djed.dcc.linker.to_clarisse import send_to_clarisse, is_clarisse_connected
from djed.utils.assets_db import AssetsDB
from djed.utils.generic import validate_name
from djed.settings import settings

# ---------------------------------
# Variables
djed_order = 34
db = AssetsDB()


# ---------------------------------
# Start Here
class Clarisse(bpy.types.Panel):
    """Creates a Clarisse Djed Panel in the 3d window"""

    bl_label = "Clarisse"
    bl_idname = "OBJECT_PT_djed_clarisse"
    bl_description = "Djed Connections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        # connection
        box = self.layout.box()
        # row = box.row()
        # row.label(text="Connection: ")
        # row.prop(context.scene, "djed_clarisse_connection", text="")

        # geometry
        row = box.row()
        row.label(text="Use Geometry as: ")
        row.prop(context.scene, "djed_clarisse_geometry", text="")

        # material
        row = box.row()
        row.label(text="Convert to material: ")
        row.prop(context.scene, "djed_clarisse_material", text="")

        # send
        row = box.row()
        row.alert = True
        row.operator("addonname.djed_send_clarisse_operator")

    def on_geometry_changed(self, context):
        current_value = context.scene.djed_clarisse_geometry
        settings.set_value(current_value, 'clarisse', 'configuration', 'geometry_type')

    def on_material_changed(self, context):
        current_value = context.scene.djed_clarisse_material
        settings.set_value(current_value, 'clarisse', 'configuration', 'use_material')

class SendToClarisse(bpy.types.Operator):
    bl_label = "Send"
    bl_idname = "addonname.djed_send_clarisse_operator"
    bl_description = "Send the selected geometry to Calrisse"

    def execute(self, context):

        if not is_clarisse_connected():
            self.report({'ERROR'}, 'Can not connect to clarisse.\n'
                                   'Make sure you open clarisse session or clarisse command port is open.')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Sending to Clarisse')

        use_latest_published = context.scene.djed_use_latest_publish

        if len(selection()) < 1:
            self.report({'WARNING'}, 'Please make sure you select an object from outliner')
            return {'CANCELLED'}

        asset_name = validate_name(selection()[0].name)

        if not use_latest_published:
            export_type = ["obj", "abc"]
            if 'usd' in context.scene.djed_clarisse_geometry.lower():
                export_type.append('usd')

            result = export_geometry(
                asset_dir=None,
                asset_name=asset_name,
                export_type=export_type
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

        to_render = context.scene.djed_clarisse_material
        to_render = '_'.join(to_render.lower().split(' '))
        colorspace = context.scene.djed_colorspace.lower()
        geometry_type = context.scene.djed_clarisse_geometry

        renderer = 'standard'

        data = {
            'name': asset_name,
            'host': 'blender',
            'family': 'asset',
            'renderer': renderer,
            'to_renderer': to_render,
            'colorspace': colorspace,
            'geometry_type': geometry_type,
            'geo_paths': geo_paths,
            'asset_data': asset_data,
        }
        send_to_clarisse(data)

        return {'FINISHED'}


classes = [
    Clarisse,
    SendToClarisse,

]


# Main Function
def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)

    geo_items = settings.get_value('geometry_type', 'clarisse', 'configuration', 'geometry_type')
    items = [(x, x, "") for x in geo_items.get('menu_items', [])]
    bpy.types.Scene.djed_clarisse_geometry = bpy.props.EnumProperty(
        name="Djed Clarisse Geometry",
        items=items,
        default=geo_items.get('value', ''),
        update=Clarisse.on_geometry_changed,
    )

    mtl_items = settings.get_value('use_material', 'clarisse', 'configuration', 'use_material')
    items = [(x, x, "") for x in mtl_items.get('menu_items', [])]
    bpy.types.Scene.djed_clarisse_material = bpy.props.EnumProperty(
        name="Djed Clarisse Material",
        items=items,
        default=mtl_items.get('value', ''),
        update=Clarisse.on_material_changed,
    )

def unregister():
    for _cls in classes:
        bpy.utils.unregister_class(_cls)

    del bpy.types.Scene.djed_clarisse_geometry
    del bpy.types.Scene.djed_clarisse_material


