# -*- coding: utf-8 -*-
"""
Documentation: Shared function for blender pipeline
"""
import os
import sys
import json
from contextlib import contextmanager
from typing import List, Iterator

import bpy

from utils.textures import ck_udim

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'src')

sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from settings.settings import get_dcc_cfg, get_textures_settings, get_colorspace_settings
from utils.file_manager import FileManager
from utils.assets_db import AssetsDB
from utils.generic import merge_dicts

fm = FileManager()
db = AssetsDB()


def show_message(message='', title='Message Box', msg_type='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=msg_type)


def save_file(filepath) -> str:
    result = bpy.ops.wm.open_mainfile(
        filepath=filepath
    )

    if result == {"FINISHED"}:
        return filepath


def get_file_path() -> str:
    filepath = bpy.data.filepath
    return filepath


def selection() -> List[bpy.types.Object]:
    return bpy.context.selected_objects


def deselect_all():
    """Deselect all object in blender"""

    active_objs = bpy.context.view_layer.objects.active
    non_object_mode_objects = []

    for obj in bpy.data.objects:
        if obj.mode != 'OBJECT':
            non_object_mode_objects.append((obj, obj.mode))
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    # revert all non object mode objects
    for obj, mode in non_object_mode_objects:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode=mode)

    # revert to active objects
    bpy.context.view_layer.objects.active = active_objs


def selected_collection() -> bpy.types.Context:
    return bpy.context.view_layer.active_layer_collection.collection


def delete_objects(objects=None):
    if objects is None:
        objects = bpy.data.objects

    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def link_to_collection(objects: List[bpy.types.Object], collection_name):
    """Link objects to collection"""

    # create collection
    djed_collection = bpy.data.collections.get(collection_name)
    if not djed_collection:
        djed_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(djed_collection)

    for obj in objects:
        source_collection = obj.users_collection[0]
        djed_collection.objects.link(obj)
        source_collection.objects.unlink(obj)


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
    return "|" + "|".join(parents)


def add_property(mesh_obj: bpy.types.Object, name: str, value=""):
    class CustomProperty(bpy.types.PropertyGroup):
        custom_property: bpy.props.StringProperty(name=name)

    mesh_data = mesh_obj.data

    mesh_data[name] = value
    bpy.utils.register_class(CustomProperty)
    bpy.types.Mesh.my_properties = bpy.props.PointerProperty(type=CustomProperty)


def add_material(objects=None, mtl_name='material', override=True, bind=True) -> bpy.types.Material:
    if objects is None:
        objects = bpy.context.selected_objects

    if mtl_name not in bpy.data.materials:
        mtl_net = bpy.data.materials.new(name=mtl_name)
        mtl_net.use_nodes = True
        # bpy.context.object.active_material = mtl_net

    else:
        mtl_net = bpy.data.materials[mtl_name]

    if not bind:
        return mtl_net

    # bind materials
    for obj in objects:
        if obj.type == 'MESH':
            try:
                if override and len(obj.material_slots) > 0:
                    obj.material_slots[0].material = mtl_net
                else:

                    obj.data.materials.append(mtl_net)
            except Exception as e:
                print(f"Can not bind material to {obj.name}\n {e}")
                # print(traceback.format_exc())
        else:
            if obj.children:
                add_material(list(get_all_children(obj))[1:], mtl_name)

    return mtl_net


def connect_nodes(network, in_node, in_name, out_node, out_name):
    in_slot = in_node.outputs[in_name]
    out_slot = out_node.inputs[out_name]
    network.node_tree.links.new(in_slot, out_slot)


def create_texture(network, tex_path, udim=False, colorspace='aces', color=False, tex_name=None):
    hdr = get_textures_settings('hdr_extension')
    extension = tex_path.rsplit('.', 1)[-1]
    if colorspace == 'aces':
        if color:
            if extension in hdr:
                cs_config = 'aces_color_hdr'
            else:
                cs_config = 'aces_color_ldr'
        else:
            cs_config = 'aces_raw'
    else:
        if color:
            cs_config = 'srgb'
        else:
            cs_config = 'raw'

    colorspace_value = get_colorspace_settings(cs_config)

    if not os.path.isfile(tex_path):
        return False

    if not tex_name:
        tex_name = os.path.basename(tex_path).split(".")[0]

    tex_node = network.node_tree.nodes.get(tex_name)

    if not tex_node:
        tex_node = network.node_tree.nodes.new('ShaderNodeTexImage')

    tex_node.name = tex_name
    img = bpy.data.images.load(tex_path)
    tex_node.image = img

    # Check UDIM
    if ck_udim(tex_path) and udim:
        tex_node.image.source = 'TILED'
    else:
        tex_node.image.source = 'FILE'

    tex_node.image.colorspace_settings.name = colorspace_value

    return tex_node


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

    filepath = get_file_path()
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

    add_material_property_to_mesh(selected[0])

    # add to database
    db.add_asset(asset_name=asset_name)
    db.add_geometry(asset_name=asset_name, source_file=get_file_path())

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
                db.add_geometry(asset_name=asset_name, obj_file=export_path + "." + ext)

            elif ext == "fbx":
                bpy.ops.export_scene.fbx(
                    filepath=export_path + '.' + ext,
                    use_visible=True,
                    use_selection=True,
                    global_scale=0.01,

                )
                db.add_geometry(asset_name=asset_name, fbx_file=export_path + "." + ext)


            elif ext == "abc":
                bpy.ops.wm.alembic_export(
                    filepath=export_path + '.' + ext,
                    selected=True,
                    flatten=False,
                    visible_objects_only=True,
                    export_custom_properties=True
                )
                db.add_geometry(asset_name=asset_name, abc_file=export_path + "." + ext)


            elif ext == "usd":
                bpy.ops.wm.usd_export(
                    filepath=export_path + '.' + ext,
                    selected_objects_only=True,
                    visible_objects_only=True,
                    generate_preview_surface=False,
                    export_textures=False,
                )
                db.add_geometry(asset_name=asset_name, usd_geo_file=export_path + "." + ext)

            export_paths[ext] = export_path + '.' + ext

    old_data = db.get_geometry(asset_name=asset_name, mesh_data="")["mesh_data"]
    old_data = json.loads(old_data)
    mesh_data = self.get_mesh_data(asset_name)
    new_data = dict(merge_dicts(old_data, mesh_data))

    db.add_geometry(asset_name=asset_name, mesh_data=json.dumps(new_data))

    return export_paths


def import_geometry(file_path: str, scale=1.0) -> List[bpy.types.Object]:
    """"Import geometry based on file extension"""

    deselect_all()

    if file_path.endswith('abc'):
        result = bpy.ops.wm.alembic_import(filepath=file_path, scale=scale)

    elif file_path.endswith('obj'):
        result = bpy.ops.wm.obj_import(filepath=file_path, global_scale=scale)

    elif file_path.endswith('fbx'):
        result = bpy.ops.wm.alembic_import(filepath=file_path, scale=scale)

    elif file_path.endswith('usd') or file_path.endswith('usdc'):
        result = bpy.ops.wm.usd_import(filepath=file_path, scale=scale, import_render=True)

    else:
        return

    if result == {'FINISHED'}:
        imported_objects = bpy.context.selected_objects
        link_to_collection(imported_objects, "DJED")
        return imported_objects


if __name__ == '__main__':
    print(__name__)
