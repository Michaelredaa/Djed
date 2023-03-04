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
sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

site.addsitedir(DJED_ROOT.joinpath('venv', 'python39', 'Lib', 'site-packages').as_posix())

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

    def process(self, instance):
        # print(instance.data)

        data = instance.data

        # import geo
        asset_name = data.get('name')
        geo_type = data.get('geometry_type', 'obj_file')
        geo_paths = data.get('geo_paths', {})
        colorspace = data.get('colorspace')

        asset_data = data.get('asset_data', {})

        geo_path = geo_paths.get(geo_type)
        if not geo_path:
            print(f'invalid geo_path: `{geo_path}`')
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
                        material_types[sg_name] = 'udim'
                        break
                    else:
                        material_types[sg_name] = 'not_udim'
                        break

        for sg_name in asset_data:

            all_master_mtl_names = get_material_type_names('unreal')
            if material_types[sg_name] == 'udim':
                to_renderer = all_master_mtl_names[0]
            else:
                to_renderer = all_master_mtl_names[1]

            plugs_conversion = get_material_attrs(self.hosts[0], to_renderer)

            # get master material path
            master_mat_path = get_dcc_cfg('unreal', 'renderers', to_renderer, 'standard_surface')

            mtl_path = mtl_root + '/' + sg_name
            if ur.assetExists(mtl_path):
                material_obj = ur.get_asset(mtl_path)
            else:
                instance_path = mtl_root + '/' + sg_name
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
                attrs = materials[mtl].get('attrs')
                for attr in attrs:
                    ...

                # create textures
                textures = materials[mtl].get('texs')
                for tex_name, tex_dict in textures.items():
                    plug_name = tex_dict.get('plugs')[0]
                    filepath = tex_dict.get('filepath')

                    if not plug_name:
                        continue

                    to_plug = plugs_conversion.get(plug_name)
                    if not to_plug:
                        continue

                    # create texture
                    game_tex_path = tex_root + '/' + tex_name
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
