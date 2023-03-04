# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
from contextlib import contextmanager
from typing import List, Iterator

import bpy

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'src')

sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from settings.settings import get_dcc_cfg
from utils.file_manager import FileManager

from dcc.blender.api.panels import show_message

fm = FileManager()


def save_file(filepath) -> str:
    result = bpy.ops.wm.open_mainfile(
        filepath=filepath
    )

    if result == {"FINISHED"}:
        return filepath


def current_file() -> str:
    filepath = bpy.data.filepath
    return filepath


def selection() -> List[bpy.types.Object]:
    return bpy.context.selected_objects


@contextmanager
def maintained_selection():
    """Maintain selection during context"""

    current_selection = selection()
    current_active = bpy.context.view_layer.objects.active
    try:
        yield
    finally:
        # clear selection
        for obj in selection():
            obj.select_set(state=False)

        for obj in current_selection:
            obj.select_set(state=True)

        bpy.context.view_layer.objects.active = current_active


def get_all_children(obj: bpy.types.Object) -> Iterator:
    """To get all children recursively"""

    yield obj
    for child in obj.children:
        # yield child
        yield from get_all_children(child)


def get_parents(obj):
    yield obj
    if obj.parent:
        # yield obj.parent
        yield from get_parents(obj.parent)


def get_obj_path(obj):
    parents = reversed([x.name for x in get_parents(obj)])
    return "|"+"|".join(parents)

def add_property(mesh_obj: bpy.types.Object, name: str, value=""):

    class CustomProperty(bpy.types.PropertyGroup):
        custom_property: bpy.props.StringProperty(name=name)

    mesh_data = mesh_obj.data

    mesh_data[name] = value
    bpy.utils.register_class(CustomProperty)
    bpy.types.Mesh.my_properties = bpy.props.PointerProperty(type=CustomProperty)


def add_material_property_to_mesh(obj):
    for child in get_all_children(obj):
        if child.type == "MESH":
            material = child.active_material
            if material:
                material_name = material.name
            else:
                material_name = 'Material'
            add_property(child, 'materialBinding', material_name)

def export_geometry(asset_dir=None, export_type=["abc"]):
    if asset_dir is None:
        asset_dir = get_dcc_cfg('maya', 'plugins', 'export_geometry', 'export_root')

    filepath = current_file()
    selected = selection()

    if not filepath:
        show_message("Please make sure you save the file first", "File not saved", "ERROR")
        return

    # current selection
    if not selected:
        show_message("Please make sure you select outliner object first", "No Selection", "ERROR")
        return

    asset_name = selected[0].name

    resolved_context = {
        'relatives_to': filepath,
        'variables': {'$asset_name': asset_name, '$selection': asset_name}
    }

    export_dir = fm.resolve_path(source_path=asset_dir, **resolved_context)

    fm.make_dirs(export_dir)
    export_path, version = fm.version_folder_up(export_dir)
    fm.make_dirs(export_path)
    export_path += f"/{asset_name}"

    add_material_property_to_mesh(selected)

    export_paths = {}
    with maintained_selection():

        selected[0].select_set(state=True)
        for s in get_all_children(selected[0]):
            s.select_set(state=True)

        for ext in export_type:
            if ext == "obj":
                bpy.ops.wm.obj_export(
                    filepath=export_path + '.' + ext,
                    export_selected_objects=True,
                    export_materials=True,
                    export_material_groups=True,
                )

            elif ext == "fbx":
                bpy.ops.export_scene.fbx(
                    filepath=export_path + '.' + ext,
                    use_visible=True,
                    use_selection=True,
                    global_scale=0.01,

                )

            elif ext == "abc":
                bpy.ops.wm.alembic_export(
                    filepath=export_path + '.' + ext,
                    selected=True,
                    flatten=False,
                    visible_objects_only=True,
                    export_custom_properties=True
                )

            elif ext == "usd":
                bpy.ops.wm.usd_export(
                    filepath=export_path + '.' + ext,
                    selected_objects_only=True,
                    visible_objects_only=True,
                    generate_preview_surface=False,
                    export_textures=False,
                )

            export_paths[ext] = export_path + '.' + ext

    return export_paths

if __name__ == '__main__':
    print(__name__)
