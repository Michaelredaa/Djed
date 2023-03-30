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

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

###############################
import importlib
import djed.utils.generic
import djed.dcc.maya.api.cmds
import djed.utils.file_manager

importlib.reload(djed.utils.generic)
importlib.reload(djed.dcc.maya.api.cmds)
importlib.reload(djed.utils.file_manager)

################################

import pyblish.api
from djed.dcc.maya.api.cmds import Maya
from djed.settings.settings import (
    material_attrs_conversion,
    shading_nodes_conversion,
    get_material_attrs,
    get_shading_nodes,
)

from djed.utils.file_manager import FileManager
from djed.utils.logger import Logger

import maya.cmds as cmds
import maya.mel as mel


# ---------------------------------
# Variables

# ---------------------------------
# Start Here
class LoadAsset(pyblish.api.InstancePlugin):
    label = "import and set the asset"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["asset"]

    def __init__(self):
        self.log = Logger(
            name=self.hosts[0] + self.__class__.__name__,
            use_file=True
        )

    def process(self, instance):
        self.log.debug(f"Loading asset `{instance.name}` in maya...")

        ma = Maya()
        fm = FileManager()
        asset_name = instance.name
        data = instance.data

        # import geo
        geo_type = data.get('geometry_type', '')
        import_type = data.get('import_type', '<none>')
        geo_paths = data.get('geo_paths', {})
        colorspace = data.get('colorspace')

        geo_path = geo_paths.get(geo_type)
        self.log.debug(f"geometry_type:  `{geo_type}` ->> import_type:  `{import_type}` ->> geo_paths:  `{geo_paths}`")
        self.log.debug(f"Use geo path:  {geo_path}")
        if geo_path:
            if import_type == 'Import Geometry':
                ma.import_geo(geo_path)

        # host
        source_host = data.get('host', 'standard')
        if source_host == 'spp':
            source_host = 'standard'
        host = 'maya'

        # renderer
        to_renderer = data.get('to_renderer')
        source_renderer = data.get('source_renderer', 'standard')
        self.log.debug(f"Host: `{host}` -  To renderer:  `{to_renderer}`")
        self.log.debug(f"Source host:  `{source_host}` - Source renderer:  `{source_renderer}`")

        # conversions
        if source_host == 'standard' or source_renderer == 'standard':
            # standard material
            self.log.debug(f"Using standard materials")
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
            self.log.debug(f"__sg: {sg}")

            # materials
            materials = asset_data.get(sg, {}).get('materials', {})
            for mtl in materials:
                mtl_name = re.sub(r'(?i)sg', 'MTL', sg)
                if not mtl_name.endswith('MTL'):
                    mtl_name += 'MTL'
                self.log.debug(f"__mtl: {mtl} -> __material name {mtl_name}")

                if not cmds.objExists(sg):
                    self.log.debug(f"__Creating new shading group")
                    mtl_name, sg = ma.create_material(name=mtl_name, sg=sg)
                else:
                    self.log.debug(f"__Use existence shading group")
                    exist_materials = ma.get_materials_from_sg(sg, 'material')
                    if exist_materials and mtl_name in exist_materials:
                        self.log.debug(f"__Use existence material")
                        mtl_name = exist_materials[0]
                    else:
                        self.log.debug(f"__Creating new material")
                        mtl_name, sg = ma.create_material(name=mtl, sg=sg)

                # attributes
                attrs = materials[mtl].get('attrs', {})
                self.log.debug(f"__Set attributes: {attrs}")
                for attr in attrs:
                    try:
                        to_attr = plugs_conversion.get(attr).get('name', '')
                        value = attrs.get(attr)
                        if isinstance(value, list):
                            cmds.setAttr(f'{mtl_name}.{to_attr}', *value, type='double3')
                        elif isinstance(value, str):
                            cmds.setAttr(f'{mtl_name}.{to_attr}', value, type='string')
                        else:
                            cmds.setAttr(f'{mtl_name}.{to_attr}', value)
                    except:
                        self.log.error(f"__Cant set attr {mtl_name}.{to_attr} with {value}")

                # create textures
                textures = materials[mtl].get('texs')
                self.log.debug(f"__import textures: {textures}")
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
                    self.log.debug(f"__Creating: {tex_name} -> {colorspace} -> udim {tex_dict.get('udim')}")
                    tex_node = ma.import_texture(
                        tex_dict.get('filepath'),
                        tex_dict.get('udim'),
                        colorspace,
                        plug_type == 'color',
                        tex_name

                    )

                    if plug_type == 'float':
                        tex_plug = 'outColor.outColorR'
                        cmds.setAttr(tex_node + ".alphaIsLuminance", 1)
                    else:
                        tex_plug = 'outColor'
                        mel.eval(f'generateUvTilePreview {tex_node};')

                    # inbetween nodes
                    self.log.debug(f"__Creating inbetween nodes..")
                    connected_node = tex_node
                    connected_plug = tex_plug
                    for inbetween_dict in to_plug.get("inbetween"):
                        if inbetween_dict == [{}] or not inbetween_dict:
                            continue
                        inbetween_node = mtl + inbetween_dict.get('name')

                        self.log.debug(f"__Inbetween node: {inbetween_node}")
                        if not cmds.objExists(inbetween_node):
                            inbetween_node = ma.create_util_node(inbetween_dict.get('type'), inbetween_node)
                        ma.connect_attr(
                            f'{connected_node}.{connected_plug}',
                            f'{inbetween_node}.{inbetween_dict.get("inplug")}'
                        )
                        connected_node = inbetween_node
                        connected_plug = inbetween_dict.get("outplug")

                    ma.connect_attr(
                        f'{connected_node}.{connected_plug}',
                        f'{mtl_name}.{to_plug.get("name")}')

            # displacement
            displacements = asset_data.get(sg, {}).get('displacements', {})
            self.log.debug(f"__Creating displacements: {displacements}")
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
            self.log.debug(f"__Assigning materials: {sg} -> {meshes}")
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
