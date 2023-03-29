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
import addon_utils

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

###############################
import importlib
import djed.utils.generic
import djed.utils.file_manager

importlib.reload(djed.utils.generic)
importlib.reload(djed.utils.file_manager)

################################

import pyblish.api
from djed.dcc.blender.api.pipeline import *
from djed.settings.settings import material_attrs_conversion, shading_nodes_conversion, get_material_attrs, get_shading_nodes
from djed.utils.file_manager import FileManager
from djed.utils.logger import Logger

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

    def __init__(self):
        self.log = Logger(
            name=self.hosts[0] + self.__class__.__name__,
            use_file=True
        )

    def process(self, instance):

        self.log.debug(f"create instance for {instance.name}")

        asset_name = instance.name
        data = instance.data

        # import geo
        geo_type = data.get('geometry_type', '')
        import_type = data.get('import_type', '<none>')
        geo_paths = data.get('geo_paths', {})
        colorspace = data.get('colorspace')

        geo_path = geo_paths.get(geo_type)
        self.log.debug(f"Use geo path:  {geo_path}")
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
        self.log.debug(f"Host: {host} -  To renderer:  {to_renderer}")

        source_renderer = data.get('source_renderer', 'standard')
        self.log.debug(f"Source host:  {source_host} - Source renderer:  {source_renderer}")

        # conversions
        if source_host == 'standard' or source_renderer == 'standard':
            self.log.debug(f"Using standard materials")
            # standard material
            plugs_conversion = get_material_attrs(host, to_renderer)
            nodes_conversion = get_shading_nodes(host, to_renderer)
        else:
            plugs_conversion = material_attrs_conversion(source_host, source_renderer, host, to_renderer)
            nodes_conversion = shading_nodes_conversion(source_host, source_renderer, host, to_renderer)

        self.log.debug(f"plugs_conversion: {plugs_conversion}")
        self.log.debug(f"nodes_conversion: {nodes_conversion}")

        asset_data = data.get('asset_data')
        self.log.debug(f"Processing: {asset_data}")
        for sg in asset_data:

            mtl_net = add_material(mtl_name=re.sub(r'(?i)sg', 'MTL', sg), bind=False)
            mtl_node = None

            material_output_node = mtl_net.node_tree.nodes.get('Material Output')
            if not material_output_node:
                material_output_node = mtl_net.node_tree.nodes.new('ShaderNodeOutputMaterial')
            material_output_node.location.x = 600
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

                mtl_node.location.x = 0

                connect_nodes(mtl_net, mtl_node, 'BSDF', material_output_node, 'Surface')

                # attributes
                attrs = materials[mtl].get('attrs')
                for attr in attrs:
                    to_attr = plugs_conversion.get(attr).get('name')
                    value = attrs.get(attr)

                    mtl_node.inputs[to_attr].default_value = value

                # create textures
                padding = 400
                x, y = -1*padding, 0
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
                    tex_node.location.x = x
                    tex_node.location.y = y
                    y -= 160

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

                        # position

                        inbetween_node.location.x = connected_node.location.x
                        inbetween_node.location.y = connected_node.location.y + inbetween_node.height/2
                        connected_node.location.x = connected_node.location.x-padding

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


            # displacement
            displacements = asset_data.get(sg, {}).get('displacements', {})
            for displacement, displacement_dict in displacements.items():

                if bpy.context.scene.render.engine != 'CYCLES':
                    continue

                if mtl_node:
                    mtl_net.cycles.displacement_methode = 'BOTH'

                # create displacement
                displacement_node = mtl_net.node_tree.nodes.get(displacement)
                if not displacement_node:
                    displacement_node = mtl_net.node_tree.nodes.new("ShaderNodeDisplacement")

                displacement_node.name = displacement

                displacement_node.location.x = 300
                y_pos = -1*mtl_node.height - 600
                displacement_node.location.y = y_pos

                for tex_name, tex_dict in displacement_dict.get('texs', {}).items():
                    # create texture
                    if colorspace is None:
                        colorspace = tex_dict.get('colorspace', 'aces')
                    tex_node = create_texture(
                        mtl_net,
                        tex_dict.get('filepath'),
                        tex_dict.get('udim'),
                        colorspace,
                        False,
                        tex_name
                    )

                    # position
                    tex_node.location.y = y_pos

                    if not tex_node:
                        continue
                    connect_nodes(
                        mtl_net,
                        tex_node, 'Color',
                        displacement_node, 'Height'
                    )
                    connect_nodes(
                        mtl_net,
                        displacement_node, 'Displacement',
                        material_output_node, 'Displacement'
                    )




            # # assign materials
            # if not geo_path:
            #     continue
            # meshes = asset_data.get(sg, {}).get('meshes', {}).get('shape', {})
            # for mesh_path in meshes:
            #     try:
            #         mesh_path = '*' + mesh_path.split('|', 2)[-1]
            #         ma.assign_material(cmds.ls(mesh_path), sg_name=sg)
            #     except:
            #         pass


# Main Function
def main():
    pyblish.api.register_host("maya")
    pyblish.api.register_plugin(LoadAsset)

    context = pyblish.util.collect()

    LoadAsset().process(context[0])
    instance = pyblish.util.extract(context)


if __name__ == '__main__':
    main()
