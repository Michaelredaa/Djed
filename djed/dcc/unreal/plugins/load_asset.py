# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import os
import re
import sys
import site
import traceback
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.joinpath('djed').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

site.addsitedir(DJED_ROOT.joinpath('venv', 'python', 'Lib', 'site-packages').as_posix())

import pyblish.api

#############################################################################
import importlib
import settings.settings

importlib.reload(settings.settings)
#############################################################################


from settings.settings import (
    get_dcc_cfg,
    get_material_attrs,
    get_material_type_names

)
from djed.utils.logger import Logger

import dcc.unreal.api.pipeline as ur
importlib.reload(ur)

# ---------------------------------
# Variables

# ---------------------------------
# Start Here

class LoadAsset(pyblish.api.InstancePlugin):
    label = "import and set the asset"
    order = pyblish.api.ExtractorOrder
    hosts = ["unreal"]
    families = ["asset"]

    def __init__(self):
        self.log = Logger(
            name=self.hosts[0] + self.__class__.__name__,
            use_file=True
        )
    def process(self, instance):
        self.log.debug(f"Loading asset `{instance.name}` in unreal...")

        data = instance.data

        # import geo
        asset_name = data.get('name')
        geo_type = data.get('geometry_type', 'obj_file')
        geo_paths = data.get('geo_paths', {})
        colorspace = data.get('colorspace')

        asset_data = data.get('asset_data', {})

        geo_path = geo_paths.get(geo_type)

        self.log.debug(f"geometry_type:  `{geo_type}` ->> geo_paths:  `{geo_paths}`")
        self.log.debug(f"Use geo path:  {geo_path}")

        if not geo_path:
            self.log.error(f'invalid geo_path: `{geo_path}`')
            return

        # create root
        asset_root = get_dcc_cfg('unreal', 'configuration', 'asset_root')
        mtl_root = get_dcc_cfg('unreal', 'configuration', 'material_root')
        tex_root = get_dcc_cfg('unreal', 'configuration', 'texture_root')

        # resolve paths
        asset_root = asset_root.replace("$assetName", asset_name)
        mtl_root = mtl_root.replace('..', asset_root)
        tex_root = tex_root.replace('..', asset_root)
        ur.createDir(asset_root)

        # import asset
        prefix = 'ST'
        import_result = ur.importStaticMesh(
            filepath=geo_path,
            destination_path=asset_root,
            prefix=f'{prefix}_{asset_name}',
            scale=1,
            import_materials=False,
            combine_meshes=True,
            generate_lightmap_u_vs=True,
        )
        asset_path = ''
        for asset_path in import_result[0]:
            ur.spawn_asset(asset_path)

        # Get the master material type
        material_types = {}
        for sg_name in asset_data:
            materials = asset_data.get(sg_name, {}).get('materials', {})
            for mtl in materials:
                textures = materials[mtl].get('texs')
                for tex_name, tex_dict in textures.items():
                    udim = tex_dict.get('udim')
                    if int(udim) > 1:
                        self.log.debug(f"Using udim for material `{sg_name}`")
                        material_types[sg_name] = 'udim'
                        break
                    else:
                        self.log.debug(f"Using non-udim for material `{sg_name}`")
                        material_types[sg_name] = 'not_udim'
                        break

        for sg_name in asset_data:
            self.log.debug(f"__sg: {sg_name}")

            all_master_mtl_names = get_material_type_names('unreal')
            if material_types[sg_name] == 'udim':
                to_renderer = all_master_mtl_names[0]
            else:
                to_renderer = all_master_mtl_names[1]

            plugs_conversion = get_material_attrs(self.hosts[0], to_renderer)
            self.log.debug(f"__plugs_conversion: {plugs_conversion}")

            # get master material path
            master_mat_path = get_dcc_cfg('unreal', 'renderers', to_renderer, 'standard_surface')
            self.log.debug(f"__using master material: {master_mat_path}")

            mtl_path = mtl_root + '/' + sg_name
            if ur.assetExists(mtl_path):
                self.log.debug(f"__Use existence material `{mtl_path}`")
                material_obj = ur.get_asset(mtl_path)
            else:
                instance_path = mtl_root + '/' + sg_name
                self.log.debug(f"__Creating new material `{instance_path}`")

                if material_types[sg_name] == 'udim':
                    material_obj = ur.makeMaterialInstance(master_mat_path, instance_path)
                    # material = ur.createMaterial(mtl_root + '/' + sg_name)
                elif material_types[sg_name] == 'not_udim':
                    material_obj = ur.makeMaterialInstance(master_mat_path, instance_path)

            # bind material to geometry
            ur.assignMaterial(asset_path, material_obj, slot_name=sg_name)

            materials = asset_data.get(sg_name, {}).get('materials', {})


            for mtl in materials:
                # attributes
                attrs = materials[mtl].get('attrs', {})
                self.log.debug(f"__Set attributes: {attrs}")
                for attr in attrs:
                    ...

                # create textures
                textures = materials[mtl].get('texs', {})
                self.log.debug(f"__import textures: {textures}")
                for tex_name, tex_dict in textures.items():
                    plug_name = tex_dict.get('plugs')[0]
                    filepath = tex_dict.get('filepath')

                    if not plug_name:
                        continue

                    to_plug = plugs_conversion.get(plug_name)
                    if not to_plug:
                        continue

                    # create texture
                    game_tex_path = tex_root+'/'+tex_name
                    self.log.debug(f"__Creating: {game_tex_path} -> {colorspace} -> udim: {tex_dict.get('udim')}")
                    if ur.assetExists(game_tex_path):
                        tex_result = [ur.get_asset(game_tex_path)]
                    else:
                        tex_result = ur.importTexture(
                            filepath,
                            tex_root,
                            virtual_texture=material_types[sg_name] == 'udim'
                        )[0]

                    if not tex_result:
                        continue

                    tex_obj = tex_result[0]

                    ur.setMaterialInstanceTexture(material_obj, to_plug.get("name"), tex_obj)


        print(f'import_result: {type(import_result[0])}')


if __name__ == '__main__':
    print(__name__)
