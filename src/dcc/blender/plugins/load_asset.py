# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys
from pathlib import Path
import re

import bpy

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

###############################
import importlib
import utils.generic
import utils.file_manager

importlib.reload(utils.generic)
importlib.reload(utils.file_manager)

################################

import pyblish.api
from dcc.blender.api.pipeline import *
from settings.settings import material_attrs_conversion, shading_nodes_conversion, get_material_attrs, get_shading_nodes
from utils.file_manager import FileManager

# ---------------------------------
# Variables
fm = FileManager()


# ---------------------------------
# Start Here
class LoadAsset(pyblish.api.InstancePlugin):
    label = "import and set the asset"
    order = pyblish.api.ExtractorOrder
    hosts = ["blender"]
    families = ["asset"]

    def process(self, instance):

        asset_name = instance.name
        data = instance.data

        # import geo
        geo_type = data.get('geometry_type', '')
        import_type = data.get('import_type', '<none>')
        geo_paths = data.get('geo_paths', {})
        colorspace = data.get('colorspace')

        geo_path = geo_paths.get(geo_type)
        if geo_path:
            if import_type == 'Import Geometry':
                import_geometry(geo_path, scale=1.0)

        # host
        source_host = data.get('host', 'standard')
        if source_host == 'spp':
            source_host = 'standard'
        host = 'blender'

        # renderer
        to_renderer = data.get('to_renderer')

        source_renderer = data.get('source_renderer', 'standard')

        # conversions
        if source_host == 'standard' or source_renderer == 'standard':
            # standard material
            plugs_conversion = get_material_attrs(host, to_renderer)
            nodes_conversion = get_shading_nodes(host, to_renderer)
        else:
            plugs_conversion = material_attrs_conversion(source_host, source_renderer, host, to_renderer)
            nodes_conversion = shading_nodes_conversion(source_host, source_renderer, host, to_renderer)

        asset_data = data.get('asset_data')
        for sg in asset_data:

            mtl_net = add_material(mtl_name=sg, bind=False)

            material_output_node = mtl_net.node_tree.nodes.get('Material Output')
            if not material_output_node:
                material_output_node = mtl_net.node_tree.nodes.new('ShaderNodeOutputMaterial')
            # materials
            materials = asset_data.get(sg, {}).get('materials', {})
            for mtl in materials:
                # mtl_name = re.sub(r'(?i)sg', 'MTL', sg)
                from_renderer = materials[mtl].get('type')
                mtl_type = nodes_conversion.get(from_renderer)

                mtl_node = mtl_net.node_tree.nodes.get('Principled BSDF')
                if mtl_node:
                    mtl_node.name = mtl

                mtl_node = mtl_net.node_tree.nodes.get(mtl)
                if not mtl_node:
                    mtl_node = mtl_net.node_tree.nodes.new(mtl_type)

                connect_nodes(mtl_net, mtl_node, 'BSDF', material_output_node, 'Surface')

                # attributes
                attrs = materials[mtl].get('attrs')
                for attr in attrs:
                    to_attr = plugs_conversion.get(attr).get('name')
                    value = attrs.get(attr)

                    mtl_node.inputs[to_attr].default_value = value

                # create textures
                textures = materials[mtl].get('texs')
                for tex_name, tex_dict in textures.items():
                    plug_name = tex_dict.get('plugs')[0]
                    if not plug_name:
                        continue
                    tex_type = tex_dict.get('type')
                    to_plug = plugs_conversion.get(plug_name)
                    if not to_plug:
                        continue
                    plug_type = to_plug.get('type')  # float color, vector

                    if colorspace is None:
                        colorspace = tex_dict.get('colorspace', 'aces')
                    # create texture
                    tex_node = create_texture(
                        mtl_net,
                        tex_dict.get('filepath'),
                        tex_dict.get('udim'),
                        colorspace,
                        plug_type == 'color',
                        tex_name

                    )

                    if plug_type == 'float':
                        ...
                    else:
                        ...

                    # inbetween nodes
                    connected_node = tex_node
                    connected_plug = 'Color'
                    for inbetween_dict in to_plug.get("inbetween"):
                        if inbetween_dict == [{}] or not inbetween_dict:
                            continue
                        inbetween_node_name = inbetween_dict.get('name')

                        inbetween_node = mtl_net.node_tree.nodes.get(inbetween_node_name)
                        if not inbetween_node:
                            inbetween_node = mtl_net.node_tree.nodes.new(inbetween_dict.get('type'))
                            inbetween_node.name = inbetween_node_name

                        connect_nodes(
                            mtl_net,
                            connected_node, connected_plug,
                            inbetween_node, inbetween_dict.get("inplug")
                        )

                        connected_node = inbetween_node
                        connected_plug = inbetween_dict.get("outplug")

                    connect_nodes(
                        mtl_net,
                        connected_node, connected_plug,
                        mtl_node, to_plug.get("name")
                    )

            continue

            # displacement
            displacements = asset_data.get(sg, {}).get('displacements', {})
            for displacement, displacement_dict in displacements.items():
                # create displacement
                displacement_node = displacement
                tex_name = displacement.replace('displacement', 'height')
                if not cmds.objExists(displacement_node):
                    displacement_node = cmds.shadingNode('displacementShader', n=displacement_node, asShader=1)

                for tex_name, tex_dict in displacement_dict.get('texs', {}).items():
                    # create texture
                    if colorspace is None:
                        colorspace = tex_dict.get('colorspace', 'aces')
                    tex_node = ma.import_texture(
                        tex_dict.get('filepath'),
                        tex_dict.get('udim'),
                        colorspace,
                        False,
                        tex_name
                    )
                    if not tex_node:
                        continue
                    cmds.connectAttr(f'{tex_node}.outColor.outColorR', displacement_node + '.displacement', f=1)
                    cmds.connectAttr(displacement_node + '.displacement', f'{sg}.displacementShader', f=1)

            # assign materials
            if not geo_path:
                continue
            meshes = asset_data.get(sg, {}).get('meshes', {}).get('shape', {})
            for mesh_path in meshes:
                try:
                    mesh_path = '*' + mesh_path.split('|', 2)[-1]
                    ma.assign_material(cmds.ls(mesh_path), sg_name=sg)
                except:
                    pass

        # ma.arrangeHypershade()


# Main Function
def main():
    pyblish.api.register_host("maya")
    pyblish.api.register_plugin(LoadAsset)

    context = pyblish.util.collect()

    LoadAsset().process(context[0])
    instance = pyblish.util.extract(context)


if __name__ == '__main__':
    main()
