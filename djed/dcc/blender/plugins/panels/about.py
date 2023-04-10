# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import bpy

# ---------------------------------
# Variables
djed_order = 100


# ---------------------------------
# Start Here

class DJEDAbout(bpy.types.Panel):
    """Creates a Djed Panel in the Object properties window"""

    bl_label = "About"
    bl_idname = "OBJECT_PT_djed_about_panel"
    bl_description = "Djed About"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()


classes = [DJEDAbout, ]


# Main Function
def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def unregister():
    for _cls in classes:
        bpy.utils.unregister_class(_cls)


def main():
    register()


if __name__ == '__main__':
    main()
