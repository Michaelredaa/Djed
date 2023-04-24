# -*- coding: utf-8 -*-
"""
Documentation: Shared function for blender pipeline
"""
import os
import sys
import re
from contextlib import contextmanager
from typing import List, Iterator, Dict

import bpy

DJED_ROOT = os.getenv('DJED_ROOT')

sysPaths = [DJED_ROOT]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.settings.settings import get_dcc_cfg, get_textures_settings, get_colorspace_settings, get_material_attrs
from djed.utils.file_manager import FileManager
from djed.utils.textures import ck_udim
from djed.utils.assets_db import AssetsDB
from djed.utils.generic import validate_name
from djed.utils.logger import Logger

fm = FileManager()
db = AssetsDB()
log = Logger(name='blender_pipeline', use_file=True)


def create_context():
    _context = bpy.context.copy()
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                _context['area'] = area
                _context['screen'] = screen
                _context['window'] = window
                _context['view_layer'] = bpy.context.view_layer
                _context['selected_objects'] = bpy.context.view_layer.objects.selected

    return _context


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
    if hasattr(bpy.context, "selected_objects"):
        return bpy.context.selected_objects
    else:
        return create_context().get('selected_objects', [])


def file_colorspace():
    return bpy.context.scene.display_settings.display_device


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
    parents = reversed([validate_name(x.name) for x in get_parents(obj)])
    return "|" + "|".join(parents)


def add_property(mesh_obj: bpy.types.Object, name: str, value=""):
    name = validate_name(name)

    class CustomProperty(bpy.types.PropertyGroup):
        custom_property: bpy.props.StringProperty(name=name)

    mesh_data = mesh_obj.data

    mesh_data[name] = value
    bpy.utils.register_class(CustomProperty)
    bpy.types.Mesh.my_properties = bpy.props.PointerProperty(type=CustomProperty)


def check_uv_maps(mesh: bpy.types.Mesh):
    """To checks uv layer for each mesh and rename the first one to `map1`"""

    uv_sets = mesh.uv_layers
    if not uv_sets:
        return

    map1 = uv_sets.get('map1')

    if map1 is None:
        map1 = uv_sets[0]
        map1.name = 'map1'

    map1_index = uv_sets.find('map1')
    map1.active_render = True
    uv_sets.active_index = map1_index


def add_material(objects=None, mtl_name='material', override=True, bind=True) -> bpy.types.Material:
    if objects is None:
        objects = selection()

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


def get_mesh_data(obj):
    """To gather mesh data like material and paths"""

    data = {}
    for child in get_all_children(obj):
        if child.type == "MESH":
            mtls = obj.material_slots

            if not mtls:
                continue

            for mtl in mtls:
                mtl_name = validate_name(mtl.name)
                if mtl_name not in data:
                    data[mtl_name] = {'meshes': {}}
                if 'shape' not in data[mtl_name]['meshes']:
                    data[mtl_name]['meshes'] = {'shape': []}

                data[mtl_name]['meshes']['shape'].append(get_obj_path(obj))

                # add materials
                material_data = get_textures_from_mtl(mtl.material)
                data[mtl_name].update(material_data)

    return data


def get_standard_material_plug(plug, node='standard_surface'):
    """To get the standard plug name form settings"""
    attrs = get_material_attrs('blender', 'principle_BSDF', node=node)
    for attr in attrs:
        if attrs[attr]['name'] == plug:
            return attr
    else:
        return ''


def get_textures_from_mtl(network: bpy.types.Material) -> Dict:
    """
    To get all material connection data related to textures
    """

    def get_connected_image(node):
        for _input in node.inputs:
            if not _input.is_linked:
                continue

            for _link in _input.links:
                if _link.from_node.type == 'TEX_IMAGE':
                    return _link.from_node
                else:
                    get_connected_image(_link.from_node)

    def get_texture_path(shader_node, cfg_node='standard_surface'):
        tex_dict = {}
        for s_input in shader_node.inputs:
            if not s_input.is_linked:
                continue

            for s_link in s_input.links:
                if s_link.from_node.type == 'TEX_IMAGE':
                    image_node = s_link.from_node
                else:
                    image_node = get_connected_image(s_link.from_node)
                    if not image_node:
                        continue

                image = image_node.image
                if image and not image.is_dirty and image.packed_file:
                    filepath = image.pixels
                    # image.save_render(filepath=file_path)
                else:
                    filepath = image.filepath

                colorspace = image.colorspace_settings.name
                if colorspace == 'Non-Color':
                    colorspace = "Raw"

                # get UDIM
                if image.source == 'TILED':
                    udim = len(image.tiles)
                else:
                    udim = 0

                plug_name = get_standard_material_plug(s_link.to_socket.name, node=cfg_node)

                image_name = validate_name(image_node.name)
                tex_dict[image_name] = {}
                tex_dict[image_name]["plugs"] = [plug_name]
                tex_dict[image_name]["filepath"] = filepath
                tex_dict[image_name]["colorspace"] = colorspace
                tex_dict[image_name]["type"] = image_node.type
                tex_dict[image_name]["udim"] = udim

        return tex_dict

    def get_attrs(mtl_node):
        attrs = {}
        cfg_attrs = get_material_attrs('blender', 'principle_BSDF')
        for attr_name in cfg_attrs:
            bl_attr_name = cfg_attrs[attr_name]['name']
            attr = mtl_node.inputs.get(bl_attr_name)

            if not attr or attr.is_linked:
                continue
            value = attr.default_value

            if bl_attr_name in ['Alpha', ]:
                value = [value, value, value]

            if isinstance(value, (str, int, float)):
                attrs[attr_name] = value
            elif len(value) > 1:
                attrs[attr_name] = tuple(value)

        return attrs

    material_data = {'materials': {}, 'displacements': {}}
    material_out = [x for x in network.node_tree.nodes if x.type == 'OUTPUT_MATERIAL']

    if not material_out: return material_data

    material_out = material_out[0]
    for node_input in material_out.inputs:

        if not node_input.is_linked:
            continue

        for link in node_input.links:
            shader_node = link.from_node
            shader_node_name = validate_name(shader_node.name)

            txt = re.findall(r'(?i)mtl', shader_node_name)
            if not txt:
                shader_node_name = shader_node_name + "MTL"

            if link.to_socket.name == "Surface":
                tex_dict = get_texture_path(shader_node)
                material_data['materials'][shader_node_name] = {
                    "texs": tex_dict,
                    "attrs": get_attrs(shader_node),
                    "type": 'standard_surface',
                }

            elif link.to_socket.name == "Displacement":
                tex_dict = get_texture_path(shader_node, cfg_node='displacement')
                material_data['displacements'][shader_node_name] = {"texs": tex_dict, "type": 'displacement'}

    return material_data


def connect_nodes(network, in_node, in_name, out_node, out_name):
    in_slot = in_node.outputs[in_name]
    out_slot = out_node.inputs[out_name]
    network.node_tree.links.new(in_slot, out_slot)


def create_texture(network, tex_path, udim=False, colorspace='aces', color=False, tex_name=None, collapse=True):
    hdr = get_textures_settings('hdr_extension')
    extension = tex_path.rsplit('.', 1)[-1]
    if colorspace == 'aces' and file_colorspace() == 'ACES':
        if color:
            if extension in hdr:
                cs_config = 'aces_color_hdr'
            else:
                cs_config = 'aces_color_sdr'
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

    tex_node.name = validate_name(tex_name)
    img = bpy.data.images.load(tex_path)
    tex_node.image = img

    # Check UDIM
    if ck_udim(tex_path) and udim:
        tex_node.image.source = 'TILED'
    else:
        tex_node.image.source = 'FILE'

    tex_node.image.colorspace_settings.name = colorspace_value

    if collapse:
        tex_node.hide = True

    return tex_node


def add_material_property_to_mesh(obj):
    log.debug(f"Adding material property to all children of: {obj.name}")

    for child in get_all_children(obj):
        if child.type == "MESH":
            check_uv_maps(child.data)

            material = child.active_material
            if material:
                material_name = validate_name(material.name)
            else:
                material_name = 'Material'
            add_property(child, 'materialBinding', material_name)


def export_geometry(asset_dir=None, asset_name=None, export_type=["abc"]):
    if asset_dir is None:
        asset_dir = get_dcc_cfg('maya', 'plugins', 'export_geometry', 'export_root')

    source_file = get_file_path()
    selected = selection()
    log.debug(f"Detecting working file : `{source_file}`, {bool(source_file)}")

    if not source_file:
        show_message("Please make sure you save the file first", "File not saved", "ERROR")
        return

    # current selection
    if not selected:
        show_message("Please make sure you select outliner object first", "No Selection", "ERROR")
        return

    if asset_name is None:
        asset_name = validate_name(selected[0].name)

    log.info(f"Working on asset: `{asset_name}`")

    resolved_context = {
        'relatives_to': source_file,
        'variables': {'$asset_name': asset_name, '$selection': asset_name}
    }

    export_dir = fm.resolve_path(source_path=asset_dir, **resolved_context)
    fm.make_dirs(export_dir)
    log.debug(f"Set export path to: {export_dir}")

    export_path, version = fm.version_folder_up(export_dir)
    log.debug(f"Version export to : {version}")

    fm.make_dirs(export_path)
    export_path += f"/{asset_name}"
    log.debug(f"Final export path to: {export_path}")

    add_material_property_to_mesh(selected[0])

    # add to database
    log.debug(f"Adding to database: `{asset_name}` with source file: {source_file}")
    db.add_asset(asset_name=asset_name)
    db.add_geometry(asset_name=asset_name, source_file=source_file)

    export_paths = {}
    with maintained_selection():

        selected_object = selected[0]
        selected_object.select_set(state=True)
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
                db.add_geometry(asset_name=asset_name, obj_file=f"{export_path}.{ext}")
                log.debug(f"Adding to database: `{asset_name}` with source file: `{export_path}.{ext}`")

            elif ext == "fbx":
                bpy.ops.export_scene.fbx(
                    filepath=export_path + '.' + ext,
                    use_visible=True,
                    use_selection=True,
                    global_scale=0.01,

                )
                db.add_geometry(asset_name=asset_name, fbx_file=f"{export_path}.{ext}")
                log.debug(f"Adding to database: `{asset_name}` with source file: `{export_path}.{ext}`")

            elif ext == "abc":
                bpy.ops.wm.alembic_export(
                    filepath=export_path + '.' + ext,
                    selected=True,
                    flatten=False,
                    visible_objects_only=True,
                    export_custom_properties=True
                )
                db.add_geometry(asset_name=asset_name, abc_file=f"{export_path}.{ext}")
                log.debug(f"Adding to database: `{asset_name}` with source file: `{export_path}.{ext}`")

            elif ext == "usd":
                bpy.ops.wm.usd_export(
                    filepath=export_path + '.' + ext,
                    selected_objects_only=True,
                    visible_objects_only=True,
                    generate_preview_surface=False,
                    export_textures=False,
                )
                db.add_geometry(asset_name=asset_name, usd_geo_file=f"{export_path}.{ext}")
                log.debug(f"Adding to database: `{asset_name}` with source file: `{export_path}.{ext}`")

            export_paths[ext] = f"{export_path}.{ext}"

    data = db.get_geometry(asset_name=asset_name, mesh_data="")["mesh_data"]
    data.update(get_mesh_data(selected[0]))
    db.add_geometry(asset_name=asset_name, mesh_data=data)

    return export_paths


def import_geometry(file_path: str, scale=1.0) -> List[bpy.types.Object]:
    """"Import geometry based on file extension"""

    deselect_all()
    _context = bpy.context

    if _context.screen is None:
        _context = create_context()

    if file_path.endswith('abc'):
        result = bpy.ops.wm.alembic_import(_context, filepath=file_path, scale=scale)

    elif file_path.endswith('obj'):
        result = bpy.ops.wm.obj_import(_context, filepath=file_path, global_scale=scale)

    elif file_path.endswith('fbx'):
        result = bpy.ops.wm.alembic_import(_context, filepath=file_path, scale=scale)

    elif file_path.endswith('usd') or file_path.endswith('usdc'):
        result = bpy.ops.wm.usd_import(_context, filepath=file_path, scale=scale, import_render=True)

    else:
        return

    if result == {'FINISHED'}:
        imported_objects = selection()
        link_to_collection(imported_objects, "DJED")
        return imported_objects


if __name__ == '__main__':
    print(__name__)
