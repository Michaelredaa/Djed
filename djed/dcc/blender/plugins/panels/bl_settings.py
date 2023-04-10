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

DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.settings import settings


# ---------------------------------
# Variables
djed_order = 40

# ---------------------------------
# Start Here

class DJEDSettings(bpy.types.Panel):
    """Creates a Djed Panel in the Object properties window"""

    bl_label = "Settings"
    bl_idname = "OBJECT_PT_djed_settings_panel"
    bl_description = "Djed General Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DJED"

    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj = context.object

        # Add checkbox for latest publish
        row = layout.row()
        row.label(text="Use Latest Publish: ")
        row.prop(context.scene, "djed_use_latest_publish", text="")

        # Add ComboBox for colorspace
        row = layout.row()
        row.label(text="Colorspace: ")
        row.prop(context.scene, "djed_colorspace", text="")

    def on_use_latest_publish_changed(self, context):
        # set settings
        current_value = context.scene.djed_use_latest_publish
        settings.set_value(current_value, 'blender', 'configuration', 'use_latest_publish')

    def on_colorspace_changed(self, context):
        # set settings
        current_value = context.scene.djed_colorspace
        settings.set_value(current_value, 'blender', 'configuration', 'colorspace')


classes = [DJEDSettings, ]


# Main Function
def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)

    # Settings
    use_latest_publish = settings.get_value('use_latest_publish', 'blender', 'configuration',
                                            'use_latest_publish').get('value', True)
    bpy.types.Scene.djed_use_latest_publish = bpy.props.BoolProperty(
        default=use_latest_publish,
        update=DJEDSettings.on_use_latest_publish_changed,
    )

    # colorspace
    colorspace = settings.get_value('colorspace', 'blender', 'configuration', 'colorspace')
    items = [(x.lower(), x, f"use {x} while export") for x in colorspace.get('menu_items', [])]
    bpy.types.Scene.djed_colorspace = bpy.props.EnumProperty(
        name="Djed Colorspace",
        items=items,
        default=colorspace.get('value', '').lower(),
        update=DJEDSettings.on_colorspace_changed,
    )


def unregister():
    for _cls in classes:
        bpy.utils.unregister_class(_cls)

    del bpy.types.Scene.djed_use_latest_publish
    del bpy.types.Scene.djed_colorspace


def main():
    register()


if __name__ == '__main__':
    main()
