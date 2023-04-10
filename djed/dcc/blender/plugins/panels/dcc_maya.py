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
from djed.dcc.linker.to_maya import send_to_maya, is_maya_connected
from djed.utils.assets_db import AssetsDB
from utils.generic import validate_name
from djed.settings import settings

# ---------------------------------
# Variables
djed_order = 32
db = AssetsDB()


# ---------------------------------
# Start Here
class Maya(bpy.types.Panel):
    """Creates a Maya Djed Panel in the 3d window"""

    bl_label = "Maya"
    bl_idname = "OBJECT_PT_djed_maya"
    bl_description = "Djed Connections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        box = self.layout.box()

        # if is_maya_connected():
        #     row = box.row()
        #     row.label(text="Connected", icon="CHECKMARK")
        # else:
        #     row = box.row()
        #     row.label(text="Not Connected", icon="CANCEL")

        # geometry
        row = box.row()
        row.label(text="Use Geometry as: ")
        row.prop(context.scene, "djed_maya_geometry", text="")

        # material
        row = box.row()
        row.label(text="Convert to material: ")
        row.prop(context.scene, "djed_maya_material", text="")

        row = box.row()
        row.alert = True
        row.operator("addonname.djed_send_maya_operator")

    def on_geometry_changed(self, context):
        current_value = context.scene.djed_maya_geometry
        settings.set_value(current_value, 'maya', 'configuration', 'geometry_type')

    def on_material_changed(self, context):
        current_value = context.scene.djed_maya_material
        settings.set_value(current_value, 'maya', 'configuration', 'use_material')


class SendToMaya(bpy.types.Operator):
    bl_label = "Send"
    bl_idname = "addonname.djed_send_maya_operator"
    bl_description = "Send the selected geometry to Maya"

    def execute(self, context):

        if not is_maya_connected():
            self.report({'ERROR'}, 'Can not connect to Maya.\n'
                                   'Make sure you open Maya session or Maya command port is open.')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Sending to Maya')

        if len(selection()) < 1:
            self.report({'WARNING'}, 'Please make sure you select an object from outliner')
            return {'CANCELLED'}

        asset_name = validate_name(selection()[0].name)

        use_latest_published = context.scene.djed_use_latest_publish

        if not use_latest_published:
            export_type = ["obj", "abc"]
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

        to_render = context.scene.djed_maya_material
        import_type = context.scene.djed_maya_geometry
        colorspace = context.scene.djed_colorspace.lower()
        geometry_type = 'abc_file'
        renderer = 'standard'

        data = {
            'name': asset_name,
            'host': 'blender',
            'renderer': renderer,
            'to_renderer': to_render,
            'colorspace': colorspace,
            'geometry_type': geometry_type,
            'import_type': import_type,
            'geo_paths': geo_paths,
            'asset_data': asset_data,
        }
        send_to_maya(data)

        return {'FINISHED'}


# def check_custom_value():
#     # Redraw the user interface to update the label color
#     bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
#
#     # Return the time until the next check
#     return 50

classes = [
    Maya,
    SendToMaya,

]


# Main Function
def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)

    geo_items = settings.get_value('geometry_type', 'maya', 'configuration', 'geometry_type')
    items = [(x, x, "") for x in geo_items.get('menu_items', [])]
    bpy.types.Scene.djed_maya_geometry = bpy.props.EnumProperty(
        name="Djed Maya Geometry",
        items=items,
        default=geo_items.get('value', ''),
        update=Maya.on_geometry_changed,
    )

    mtl_items = settings.get_value('use_material', 'maya', 'configuration', 'use_material')
    items = [(x, x, "") for x in mtl_items.get('menu_items', [])]
    bpy.types.Scene.djed_maya_material = bpy.props.EnumProperty(
        name="Djed Maya Material",
        items=items,
        default=mtl_items.get('value', ''),
        update=Maya.on_material_changed,
    )

    # bpy.app.timers.register(check_custom_value)


def unregister():
    for _cls in classes:
        bpy.utils.unregister_class(_cls)

    del bpy.types.Scene.djed_maya_geometry
    del bpy.types.Scene.djed_maya_material
