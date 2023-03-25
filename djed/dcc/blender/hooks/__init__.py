# # -*- coding: utf-8 -*-
# """
# Documentation:
# """
#
# if __name__ == '__main__':
#     print(__name__)


import bpy


class SimpleOperator(bpy.types.Operator):
    """My simple operator"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Operator"

    def execute(self, context):
        print("Hello, World!")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SimpleOperator)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)


if __name__ == "__main__":
    register()
