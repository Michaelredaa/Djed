# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
import re
import site

import bpy

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'djed')

sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

site.addsitedir(os.path.join(DJED_ROOT, 'venv', 'python39', 'Lib', 'site-packages'))

import pyblish.api
import pyblish.util

import importlib
import dcc.blender.api.pipeline
import dcc.blender.api.custom_icons
import dcc.blender.plugins

importlib.reload(dcc.blender.api.pipeline)
importlib.reload(dcc.blender.api.custom_icons)
importlib.reload(dcc.blender.plugins)

from dcc.blender.api.pipeline import add_material
from dcc.blender.api.custom_icons import get_icon
from dcc.blender.plugins import CreateMaterialFromTextures, LoadAsset


class DJEDMaterials(bpy.types.Panel):
    """Creates a Djed Panel in the Object properties window"""

    bl_label = "Materials"
    bl_idname = "OBJECT_PT_djed_mtl_panel"
    bl_description = "Djed Materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()

        row.operator("addonname.djed_addmtl_operator")  # , icon_value=get_icon('shading'))

        row = layout.row()
        row.operator("addonname.djed_create_mtl_tex_operator")  # , icon_value=get_icon('mtlTexture'))

        # to get all material slots


class AddMaterial(bpy.types.Operator):
    bl_label = "Add Material"
    bl_idname = "addonname.djed_addmtl_operator"
    bl_description = "Add new material to selected. Select objects and press `Add Material`"

    def execute(self, context):  # execute() is called when running teh operator.
        # self.report({'INFO'}, 'djed_addmtl_operator')
        bpy.ops.object.input_material_field('INVOKE_DEFAULT')
        return {'FINISHED'}


class AddMaterialFromTextures(bpy.types.Operator):
    bl_label = "Create Material From Textures"
    bl_idname = "addonname.djed_create_mtl_tex_operator"
    bl_description = "Create material from textures"

    def execute(self, context):
        tex_dir = r"D:\3D\working\projects\Generic\03_Workflow\Assets\tv_table\Scenefiles\sur\Textures\v0003"

        context = pyblish.api.Context()
        instance_obj = CreateMaterialFromTextures(tex_dir)
        instance = instance_obj.process(context)
        instance.data['colorspace'] = 'srgb'
        LoadAsset().process(instance)

        return {'FINISHED'}


class MaterialTextField(bpy.types.Operator):
    bl_idname = "object.input_material_field"
    bl_label = "Quick Create Material"

    material_name: bpy.props.StringProperty(
        name="Name",
        default=""
    )

    def execute(self, context):
        # self.report({'INFO'}, f"You entered: {self.material_name}")
        if self.material_name:

            # reformat material name
            self.material_name = "".join([x.capitalize() for x in self.material_name.split("_")])
            self.material_name = self.material_name[0].lower() + self.material_name[1:]

            mtl_name = re.findall(r'(?i)mtl', self.material_name)
            if not mtl_name:
                self.material_name = self.material_name + "MTL"

            else:
                self.material_name = re.sub(r'(?i)mtl', mtl_name[0].upper(), self.material_name)

            self.material_name = self.material_name.replace('.', '')

            # bind material
            add_material(mtl_name=self.material_name)
        return {'FINISHED'}

    def invoke(self, context, event):
        # Call the dialog
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        # Create the text field
        text_item = layout.prop(self, "material_name")

    def modal(self, context, event):
        if event.type == 'RET' and event.value == 'PRESS':
            self.execute(context)
            return {'FINISHED'}
        elif event.type in {'ESC'}:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


classes = [
    DJEDMaterials,
    AddMaterial,
    MaterialTextField,
    AddMaterialFromTextures,
]


def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def unregister():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def main():
    # addon_utils.enable('node_arrange')
    # unregister()
    register()


if __name__ == "__main__":
    main()
