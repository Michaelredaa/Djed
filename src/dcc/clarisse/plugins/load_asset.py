# -*- coding: utf-8 -*-
"""
Documentation:
"""


# ---------------------------------
# Import Libraries
import os
import sys
import site
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

site.addsitedir(DJED_ROOT.joinpath('venv', 'python39', 'Lib', 'site-packages').as_posix())


##########################
import importlib
import dcc.clarisse.api.cmds
import utils.file_manager

importlib.reload(utils.file_manager)




import pyblish.api

from utils.file_manager import FileManager
from dcc.clarisse.api.cmds import Clarisse

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
        self.log.info("-initialize loading asset into clarisse")
        self.fm = FileManager()
        self.cl = Clarisse()

        asset_name = instance.name

        data = instance.data

        source_renderer = data.get('renderer')
        source_host = data.get('host')
        to_renderer = data.get('to_renderer', 'standardSurface')

        geo_paths = data.get('geo_paths')
        geo_type = data.get('geo_type', 'abc_ref')

        if geo_type in ['abc_ref', 'abc_bundle']:
            geo_path = geo_paths.get('abc')
        else:
            return


        # create contexts
        mtl_ctx = self.fm.get_user_json('clarisse', 'material_root')
        tex_ctx = self.fm.get_user_json('clarisse', 'texture_root')
        utils_ctx = self.fm.get_user_json('clarisse', 'utils_root')

        # root
        root_ctx = self.fm.get_user_json('clarisse', 'asset_root').replace("$assetName", asset_name)
        # if ix.item_exists(root_ctx):
        #     ix.ix.log_error(f"[Djed] Asset already exists at: '{root_ctx}'")
        #     return

        root_ctx = self.cl.create_context(root_ctx)

        geo_ctx = self.cl.create_context(root_ctx + "/geo")
        mtl_ctx = self.cl.create_context(mtl_ctx.replace('..', root_ctx))
        tex_ctx = self.cl.create_context(tex_ctx.replace('..', root_ctx))
        utils_ctx = self.cl.create_context(utils_ctx.replace('..', root_ctx))

        # import geometry
        geo_item = self.cl.import_geo(geo_path, asset_name, context=str(geo_ctx), geo_type=geo_type)

        asset_data = data.get('asset_data')


        material_conversion = self.fm.material_conversion(source_host, source_renderer, "clarisse", to_renderer)
        plugs_conversion = material_conversion.get('plugs')
        nodes_conversion = material_conversion.get('nodes')

        # materials
        for sg in asset_data:
            materials = asset_data.get(sg, {}).get('materials', {})

            for mtl in materials:
                from_renderer = materials[mtl].get('type')

                mtl_type = nodes_conversion.get(from_renderer).get('name')

                # create material
                mtl_node = self.cl.create_node(mtl, mtl_type, cntx=mtl_ctx)

                attrs = materials[mtl].get('attrs')
                textures = materials[mtl].get('texs')
                print(textures)
                for tex in textures:
                    print(tex)
                    plug_name = textures[tex].get('plugs')[0]
                    tex_type = textures[tex].get('type')
                    tex_path = textures[tex].get('filepath')
                    udim = textures[tex].get('filepath')
                    colorspace = ""

                    to_plug = plugs_conversion.get(plug_name)

                    if not to_plug:
                        continue

                    # create_ texture
                    tex_node = self.cl.import_texture(tex_path, tex_ctx, udim, colorspace, to_plug.get('type')=='color')
                    tex_attr = mtl_node.get_attribute(to_plug.get('name'))

                    connected_node = tex_node

                    for inbetween_dict in to_plug.get("inBetween"):
                        inbetween_node_name = mtl+inbetween_dict.get('name')

                        inbetween_node = self.cl.create_node(inbetween_node_name, inbetween_dict.get('type'), cntx=utils_ctx)
                        if not inbetween_node:
                            inbetween_node = ix.get_item(str(utils_ctx) + "/" + inbetween_node_name)

                        inbetween_node_attr = inbetween_node.get_attribute(inbetween_dict.get('inplug'))
                        ix.cmds.SetTexture([str(inbetween_node_attr)], str(connected_node))
                        connected_node = inbetween_node

                    ix.cmds.SetTexture([str(tex_attr)], str(connected_node))





            if len(materials) == 1:
                # >default
                ...

            else:
                ...






        # bundle_sgs = self.cl.get_shading_group(geo_item)
        # # shape path from bundle
        # for sg in sgs:
        #     index = sgs.get(sg)
        #     for shape in shapes:
        #         if re.search(shape, sg):
        #             ix.cmds.SetValues([str(abc_bundle) + f".materials[{index}]"], [str(mtl_node)])



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
    import sys
    import pyblish.api

    data = sys.argv[0]

    context = pyblish.api.Context()
    instance = context.create_instance(**data)

    LoadAsset().process(instance)


if __name__ == '__main__':
    main()
