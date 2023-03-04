# -*- coding: utf-8 -*-
"""
Documentation:
"""
import bpy

bl_info = {
    "name": "DJED Assets Tools",
    "category": "Object",
    "version": "0.0.0.0",
    "author": "Michael Reda"
}


def show_message(message='', title='Message Box', msg_type='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=msg_type)


class DJEDPanel(bpy.types.Panel):
    """Creates a Djed Panel in the Object properties window"""

    bl_label = "DJED"
    bl_idname = "OBJECT_PT_djed_panel"
    bl_description = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="new", icon='MATERIAL_DATA')

        row = layout.row()
        row.operator("addonname.djed_addmtl_operator")

        # to get all material slots
        material_slots = bpy.context.object.material_slots
        # print([x.name for x in material_slots])


class AddMaterial(bpy.types.Operator):
    bl_label = "Add New Material"
    bl_idname = "addonname.djed_addmtl_operator"

    def execute(self, context):  # execute() is called when running teh operator.
        self.report({'INFO'}, str(context))

        return {'FINISHED'}


classes = [DJEDPanel, AddMaterial]


def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def unregister():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def main():
    # addon_utils.enable('node_arrange')
    register()


if __name__ == "__main__":
    main()
