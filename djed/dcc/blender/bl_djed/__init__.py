
bl_info = {
    "name": "DJED Assets Tools",
    "category": "3D View",
    "version": (0, 1, 0),
    "location": "View3D > Properties > Djed",
    "author": "Michael Reda",
    "blender": (3, 4, 0),
}

import os
import importlib
import traceback

DJED_ROOT = os.getenv("DJED_ROOT")


def get_modules():
    addon_dir = os.path.join(DJED_ROOT, r"djed\dcc\blender\plugins\panels")

    modules = []
    for file_name in os.listdir(addon_dir):
        if file_name.endswith(".py") and file_name != "__init__.py":
            try:
                spec = importlib.util.spec_from_file_location(file_name[:-3], os.path.join(addon_dir, file_name))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules.append(module)
            except Exception as e:
                print("Error loading module:", file_name, e)
                print(traceback.format_exc())

    modules.sort(key=lambda x: x.djed_order)
    return modules




def register():
    for module in get_modules():
        module.register()


def unregister():
    for module in get_modules():
        module.unregister()


if __name__ == '__main__':
    register()
