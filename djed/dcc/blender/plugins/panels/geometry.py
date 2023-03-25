# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import bpy


# ---------------------------------
# Variables


# ---------------------------------
# Start Here

class DJEDGeometry(bpy.types.Panel):
    """Creates a Djed Panel in the Object properties window"""

    bl_label = "Geometry"
    bl_idname = "OBJECT_PT_djed_geo_panel"
    bl_description = "Djed Geometry"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.operator("addonname.djed_export_geos_operator", icon='CUBE')

        # to get all material slots


class ExportGeometry(bpy.types.Operator):
    bl_label = "Export Geometry"
    bl_idname = "addonname.djed_export_geos_operator"
    bl_description = "Export the selected geometry"

    def execute(self, context):  # execute() is called when running teh operator.
        self.report({'INFO'}, 'djed_export_geos_operator')

        return {'FINISHED'}


classes = [DJEDGeometry, ExportGeometry]


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
