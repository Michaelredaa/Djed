# -*- coding: utf-8 -*-
"""
Documentation:
"""

import re

from utils.file_manager import FileManager
from dcc.maya.api.cmds import Maya

import maya.cmds as cmds

fm = FileManager()
ma = Maya()


def process(instance):
    asset_name = instance.get('name')
    data = instance.get('data')

    colorspace = data.get("colorspace", "aces")
    sgs = data.get('data')
    tex_dir = data.get('texture_dir', '')
    material_type = data.get('material_type')

    if not sgs:
        sgs = fm.get_sgName_from_textures(tex_dir)

    for sg in data.get('data', []):
        if cmds.objExists(sg):
            # update if exists
            materials = ma.get_materials_from_sg(sg, 'material')
            displacements = ma.get_materials_from_sg(sg, 'displacement')

            if not materials:
                # if there is no materials connected with shading group
                mtl_name = re.sub(r'(?i)sg', 'MTL', sg)
                mtl_name, sg_name = ma.create_material(name=mtl_name, sg=sg)
                materials = [mtl_name]

            for mtl in materials:
                ma.create_material_with_texture(tex_dir, material_type, colorspace=colorspace, sg_mtl=[mtl, sg])


        else:
            mtl_name = re.sub(r'(?i)sg', 'MTL', sg)
            mtl_name, sg = ma.create_material(name=mtl_name, sg=sg)
            ma.create_material_with_texture(tex_dir, material_type, colorspace=colorspace, sg_mtl=[mtl_name, sg])


if __name__ == '__main__':
    print(__name__)
