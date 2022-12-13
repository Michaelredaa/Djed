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
import dcc.unreal.api.pipeline

importlib.reload(dcc.unreal.api.pipeline)
#############################################################################


from settings.settings import (
    get_dcc_cfg,
    material_attrs_conversion,
    shading_nodes_conversion,
    get_material_attrs,
    get_shading_nodes,

)

from dcc.unreal.api.pipeline import (
    createDir,
    importStaticMesh,
    spawn_asset,
    createMaterial,
    assignMaterial,
    assetExists,
    get_asset

)


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
        print(instance.data)

        data = instance.data

        # import geo
        asset_name = data.get('name')
        geo_type = data.get('geo_type', 'obj')
        geo_paths = data.get('geo_paths', {})
        colorspace = data.get('colorspace')

        asset_data = data.get('asset_data', {})

        geo_path = geo_paths.get(geo_type)
        if not geo_path:
            return

        # create root
        asset_root = f'/Game/Djed/Assets/{asset_name}'
        mtl_root = f'/Game/Djed/Assets/{asset_name}/mtls'
        createDir(asset_root)

        # import asset
        prefix = 'ST'
        import_result = importStaticMesh(
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
            spawn_asset(asset_path)

        for sg_name in asset_data:
            mtl_path = mtl_root + '/' + sg_name
            if assetExists(mtl_path):
                material = get_asset(mtl_path)
            else:
                material = createMaterial(mtl_root + '/' + sg_name)
            
            assignMaterial(asset_path, material, 0)
        print(f'import_result: {type(import_result[0])}')


if __name__ == '__main__':
    print(__name__)
