# -*- coding: utf-8 -*-
"""
Documentation:
"""
import bpy
import addon_utils


class DJEDPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "DJED"
    bl_idname = "OBJECT_PT_main_panel"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="new", icon='MATERIAL_DATA')

        row = layout.row()
        row.operator("addonname.addmtl_operator")

        # to get all material slots
        material_slots = bpy.context.object.material_slots
        # print([x.name for x in material_slots])


classes = [DJEDPanel]


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
