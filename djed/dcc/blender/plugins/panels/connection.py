# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
from pathlib import Path

import bpy

DJED_ROOT = Path(os.getenv("DJED_ROOT")).as_posix()

sysPaths = [DJED_ROOT]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import importlib

import dcc.linker.to_spp

importlib.reload(dcc.linker.to_spp)
#############################################################
##############################################################


from djed.dcc.linker.to_spp import send_to_spp, update_spp
from djed.utils.assets_db import AssetsDB
from djed.dcc.blender.api.pipeline import selection, export_geometry

db = AssetsDB()


# ---------------------------------
# Variables


# ---------------------------------
# Start Here

class DJEDConnections(bpy.types.Panel):
    """Creates a Djed Panel in the Object properties window"""

    bl_label = "Connections"
    bl_idname = "OBJECT_PT_djed_conn_panel"
    bl_description = "Djed Connections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj = context.object

        # add substance painter
        spp_box = layout.box()
        spp_row = spp_box.row()
        spp_row.prop(obj, "expanded_spp",
                     icon="TRIA_DOWN" if obj.expanded_spp else "TRIA_RIGHT",
                     icon_only=True, emboss=False
                     )
        spp_row.label(text="Substance Painter")

        if obj.expanded_spp:
            row = spp_box.row()
            row.operator("addonname.djed_send_spp_operator")
            row.operator("addonname.djed_update_spp_operator")

        # add unreal
        unreal_box = layout.box()
        unreal_row = unreal_box.row()
        unreal_row.prop(obj, "expanded_unreal",
                        icon="TRIA_DOWN" if obj.expanded_unreal else "TRIA_RIGHT",
                        icon_only=True, emboss=False
                        )
        unreal_row.label(text="Unreal")

        if obj.expanded_unreal:
            row = unreal_box.row()
            row.operator("addonname.djed_send_spp_operator")
            row.operator("addonname.djed_update_spp_operator")

        # add clarisse
        clarisse_box = layout.box()
        clarisse_row = clarisse_box.row()
        clarisse_row.prop(obj, "expanded_clarisse",
                          icon="TRIA_DOWN" if obj.expanded_unreal else "TRIA_RIGHT",
                          icon_only=True, emboss=False
                          )
        clarisse_row.label(text="Clarisse")

        if obj.expanded_clarisse:
            row = clarisse_box.row()
            row.operator("addonname.djed_send_spp_operator")
            row.operator("addonname.djed_update_spp_operator")

        # add maya
        maya_box = layout.box()
        maya_row = maya_box.row()
        maya_row.prop(obj, "expanded_maya",
                      icon="TRIA_DOWN" if obj.expanded_unreal else "TRIA_RIGHT",
                      icon_only=True, emboss=False
                      )
        maya_row.label(text="Maya")

        if obj.expanded_maya:
            row = maya_box.row()
            row.operator("addonname.djed_send_spp_operator")
            row.operator("addonname.djed_update_spp_operator")


class SendToSPP(bpy.types.Operator):
    bl_label = "Send"
    bl_idname = "addonname.djed_send_spp_operator"
    bl_description = "Send the selected geometry to Substance Painter"

    def execute(self, context):
        self.report({'INFO'}, 'Sending to Substance Painter')
        cfg = {}  # TODO Add custom configurations

        use_latest_published = False

        data = {}
        asset_name = selection()[0].name

        if use_latest_published:
            mesh_path = db.get_geometry(asset_name=asset_name, obj_file="")['obj_file']
        else:
            mesh_path = export_geometry(
                asset_dir=None,
                asset_name=asset_name,
                export_type=["obj", "abc"]
            )["obj"]

        data['name'] = asset_name
        data['family'] = 'asset'
        data['host'] = 'spp'
        data['mesh_path'] = mesh_path
        data['cfg'] = cfg

        send_to_spp(data)
        return {'FINISHED'}


class UpdateToSPP(bpy.types.Operator):
    bl_label = "Update"
    bl_idname = "addonname.djed_update_spp_operator"
    bl_description = "Update the selected geometry to Substance Painter"

    def execute(self, context):
        self.report({'INFO'}, 'Updating Substance Painter')
        cfg = {}  # TODO Add custom configurations

        data = {}
        asset_name = selection()[0].name

        mesh_path = export_geometry(
            asset_dir=None,
            asset_name=asset_name,
            export_type=["obj", "abc"]
        )["obj"]

        data['name'] = asset_name
        data['family'] = 'asset'
        data['host'] = 'spp'
        data['mesh_path'] = mesh_path
        data['cfg'] = cfg

        update_spp(data)

        return {'FINISHED'}


classes = [DJEDConnections, SendToSPP, UpdateToSPP]


# Main Function
def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def unregister():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def main():
    # addon_utils.enable('node_arrange')
    register()


if __name__ == '__main__':
    main()
