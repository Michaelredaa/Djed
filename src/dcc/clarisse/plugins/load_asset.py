# -*- coding: utf-8 -*-
"""
Documentation:
"""


# ---------------------------------
# Import Libraries
import os
import sys
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import pyblish.api

from utils.file_manager import FileManager

import ix

# ---------------------------------
# Variables

# ---------------------------------
# Start Here

def create_instance(data):
    context = pyblish.api.Context()
    instance = context.create_instance(**data)
    return instance

class LoadAsset(pyblish.api.InstancePlugin):
    label = "import and set the asset"
    order = pyblish.api.ExtractorOrder
    hosts = ["clarisse"]
    families = ["asset"]

    def process(self, instance):
        print(instance)
        asset_name = instance.name
        print('name: ', asset_name)
        data = instance.data
        print('data: ', data)


# ---------------------------------
# Variables


# ---------------------------------
# Start Here
class AssetLoader():

    def __init__(self):
        self.fm = FileManager()

        self.working_colorspace = 'aces'

        self.material_conversion('aistd', 'adstd')
        self.geo_type("Alembic Reference")

        self.asset_name = "assetName"

    def process(self, instance):
        asset_name = instance.get('name')
        data = instance.get('data')

        colorspace = data.get('colorspace', 'aces')
        source_renderer = data.get('source_renderer')
        dist_renderer = data.get('dist_renderer', 'standardSurface')

        # get mesh
        geo_type = data.get('geo_type')
        mesh_files = data.get('mesh_files')

        usd_path = mesh_files.get('usd_geo_file', '')


        if geo_type == 'abc_ref':
            geo_path = mesh_files.get('abc_file', '')
        elif geo_type == 'abc_bundle':
            geo_path = mesh_files.get('abc_file', '')
        elif geo_type == 'usd_ref':
            geo_path = mesh_files.get('usd_geo_file', '')
        elif geo_type == 'usd_bundle':
            geo_path = mesh_files.get('usd_geo_file', '')












    def set_colorspace(self, node, path):
        """
        To set the colorspace to node
        :param node:
        :return:
        """
        if not node:
            return

        color = self.fm.ck_tex(os.path.basename(path)) == "baseColor"
        # colorspace
        hdr = self.fm.get_cfg('hdr')
        if self.working_colorspace == 'aces':
            cs_h = self.fm.get_cfg('colorspace')['aces_color_hdr']
            cs_l = self.fm.get_cfg('colorspace')['aces_color_ldr']
            cs_r = self.fm.get_cfg('colorspace')['aces_raw']

            if color:
                if path.rsplit('.', 1)[-1] in hdr:
                    node.attrs.file_color_space[0] = cs_h
                else:
                    node.attrs.file_color_space[0] = cs_l
            else:
                node.attrs.file_color_space[0] = cs_r

        else:
            cs_h = self.fm.get_cfg('colorspace')['srgb']
            cs_r = self.fm.get_cfg('colorspace')['raw']

            if color:
                node.attrs.file_color_space[0] = cs_h
            else:
                node.attrs.file_color_space[0] = cs_r

    def material_conversion(self, _from, _to):
        '''
        convert from material type of dcc to clarisse material type
        :param _from: # aiStandardSurface
        :param _to: # MaterialPhysicalAutodeskStandardSurface
        :return:
        '''
        self.working_mtl_conversion = [_from, _to]

    def set_material(self, mtl=None):
        if mtl:
            return mtl
        else:
            return 'MaterialPhysicalAutodeskStandardSurface'


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
