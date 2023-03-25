# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys

import bpy
import bpy.utils.previews

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'src')

sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import dcc.blender.plugins.panels.materials as mtls
import dcc.blender.plugins.panels.geometry as geos
import dcc.blender.plugins.panels.connection as conn

import importlib

importlib.reload(mtls)
importlib.reload(geos)
importlib.reload(conn)

bl_info = {
    "name": "DJED Assets Tools",
    "category": "Object",
    "version": (0, 1, 0),
    "author": "Michael Reda",
    "blender": (3, 4, 0),
}

# # add icons
# icons_dict = bpy.utils.previews.new()
#
# icons_dict.load("custom_icon", icon_path, 'IMAGE')
#
# row.operator("addonname.djed_addmtl_operator", icon_value=icons_dict["custom_icon"].icon_id)


classes = []
classes.extend(mtls.classes)
classes.extend(geos.classes)
classes.extend(conn.classes)


def register():
    for _cls in classes:
        bpy.utils.register_class(_cls)

    bpy.types.Object.expanded_spp = bpy.props.BoolProperty(default=True)
    bpy.types.Object.expanded_unreal = bpy.props.BoolProperty(default=True)
    bpy.types.Object.expanded_clarisse = bpy.props.BoolProperty(default=True)
    bpy.types.Object.expanded_maya = bpy.props.BoolProperty(default=True)


def unregister():
    for _cls in classes:
        bpy.utils.register_class(_cls)


def main():
    # addon_utils.enable('node_arrange')
    register()


if __name__ == "__main__":
    main()
