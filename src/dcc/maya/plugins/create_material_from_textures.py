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
sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import pyblish.api
import pyblish.util

# from dcc.maya.api.cmds import Maya
from utils.file_manager import FileManager
from utils.textures import list_textures, ck_udim, get_sgName_from_textures, texture_type_from_name


# ---------------------------------
# Variables
fm = FileManager()

# ---------------------------------
# Start Here
class CreateMaterialFromTextures(pyblish.api.ContextPlugin):
    label = "Create material based on texture in directory"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    families = ["asset"]

    def __init__(self, directory):
        self.directory = directory

    def process(self, context):
        # ma = Maya()
        textures = list_textures(self.directory)
        sgs = get_sgName_from_textures(self.directory)
        asset_data = {}

        for sg in sgs:
            asset_data[sg] = {}
            texs_dict = {}
            for tex in textures:
                if sg in tex:
                    tex_name = sg + tex.split(sg)[-1].split('.')[0]
                    tex_plug = texture_type_from_name(tex)
                    if ck_udim(tex):
                        if not re.search(r"\.1001\.", tex):
                            continue
                        udim = 1
                    else:
                        udim = 0

                    texs_dict[tex_name] = {
                        'plugs': [tex_plug],
                        'udim': udim,
                        'type': 'file',
                        'filepath': os.path.join(self.directory, tex).replace('\\', '/')
                    }

                    if tex_plug == 'height':
                        texs_dis_dict = {
                            'plugs': [tex_plug],
                            'udim': udim,
                            'type': 'file',
                            'filepath': os.path.join(self.directory, tex).replace('\\', '/')
                        }

                        asset_data[sg]["displacements"] = {
                            sg+"_displacement": {
                                'type': "displacement",
                                "attrs": {},
                                "texs": {tex_name: texs_dis_dict}
                            }
                        }
                        continue

            asset_data[sg]["materials"] = {}
            mtl_name = re.sub(r'(?i)sg', 'MTL', sg)
            asset_data[sg]["materials"][mtl_name] = {
                "type": "standardSurface",
                "attrs": {},
                "texs": texs_dict

            }
        instance = context.create_instance(
            name='any',
            family="asset",
            colorspace='aces',
            to_renderer='arnold',
            host="standard",
            asset_data=asset_data
        )

        return instance


# Main Function
def main():
    pyblish.api.register_host("maya")
    pyblish.api.register_plugin(CreateMaterialFromTextures)
    instance = pyblish.util.collect()[0]


if __name__ == '__main__':
    main()
