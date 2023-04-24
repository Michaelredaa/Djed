# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import re
import sys
import os
from pathlib import Path
from urllib.parse import unquote

import ix

DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.joinpath('djed').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.file_manager import FileManager
from utils.decorators import error
from settings.settings import get_dcc_cfg, get_value, get_textures_settings, get_colorspace_settings, get_shading_nodes


# ---------------------------------
# Variables


# ---------------------------------
# Start Here
class Clarisse:
    @error(name=__name__)
    def __init__(self):
        self.material_type = None
        self.fm = FileManager()

    @error(name=__name__)
    def set_material_type(self, mtl_type=None):
        if mtl_type:
            self.material_type = mtl_type
        else:
            self.material_type = 'MaterialPhysicalAutodeskStandardSurface'

    @error(name=__name__)
    def create_context(self, cntx, ckExsit=True, override=False):
        """ this methode create context and check if existence to skip or override by delete if exist and create new"""
        _name, _contex = cntx.rsplit('/', 1)
        if ckExsit:
            if not ix.item_exists(_name):
                self.create_context(_name)
            if not ix.item_exists(cntx):
                cntx = ix.cmds.CreateContext(str(_contex), 'Global', _name)
            else:
                cntx = ix.get_item(cntx)

        if override:
            ix.cmds.DeleteItems([str(cntx)])
            cntx = ix.cmds.CreateContext(str(_contex), 'Global', _name)
        return str(cntx)

    @error(name=__name__)
    def create_node(self, name='_MTL#', material_type='', cntx='cntx'):

        cntx_path = self.create_context(cntx)
        node_path = ix.item_exists(f'{cntx_path}/{name}')
        if not node_path:
            node_path = ix.cmds.CreateObject(str(name), material_type, 'Global', str(cntx_path))
            return node_path
        else:
            return ix.get_item(f'{cntx_path}/{name}')

    @error(name=__name__)
    def assign_material(self, objects, mtl_name):
        """
        TO assign materials to objects by given material name or shading group name
        :param objects: (list) list of objetcs paths
        :param mtl_name: (str) the material name
        :return:(bool) the status of assignment
        """
        for obj in objects:
            obj_item = ix.get_item(obj)
            obj_item.attrs.materials = mtl_name

        return True

    @error(name=__name__)
    def get_property(self, geometryShape, prop_name):
        # search the property
        properties = geometryShape.get_module().get_properties()
        property = None
        for i in range(properties.get_property_count()):
            if properties.get_property(i).get_name() == prop_name:
                property = properties.get_property(i)
                break
        if property is None:
            return ""
        resource = property.get_values_property(0)
        string_prop = resource.get_string(0)

        values = []
        str_end = 0
        # iterate over all string values
        for i in range(property.get_value_count()):
            str_start = str_end
            # compute string size
            str_end = str_end + resource.get_item_value_count(i)
            values.append(string_prop[str_start:str_end])

        return values[0]

    @error(name=__name__)
    def get_objects_by_type(self, _objType, root):
        """
        :param _objType: any project item or the dataType
        :param root: apply on all children of contex
        :return: objects arrayu
        """
        root = ix.get_item(root)
        flags = ix.api.CoreBitFieldHelper()
        objects = ix.api.OfObjectArray()
        root.get_all_objects(str(_objType), objects, flags, False)

        return objects

    def create_ref(self, cntx, name, path, update_existence=True):
        if ix.item_exists(f'{cntx}/{name}_ref') and update_existence:
            ref_cntx = ix.get_item(f'{cntx}/{name}_ref')
        else:
            ref_cntx = ix.cmds.CreateCustomContext(name + "_ref", "Reference", "", str(cntx))

        if not ref_cntx:
            raise "Can not load asset as a reference"
        ix.cmds.SetReferenceFilenames([ix.get_item(str(ref_cntx))], [1, 0], [path])
        return ref_cntx

    def abc_bundle(self, cntx, name, path, update_existence=True):

        bundle_item = f'{cntx}/{name}_abndl'
        if ix.item_exists(bundle_item) and update_existence:
            bundle_item = ix.get_item(bundle_item)
        else:
            bundle_item = ix.cmds.CreateObject(name + "_abndl", "GeometryBundleAlembic", "Global", str(cntx))

        if not bundle_item:
            raise "Can not load asset as a abc bundle"
        ix.cmds.SetValues([str(bundle_item) + ".filename[0]"], [str(path)])
        return bundle_item

    def usd_bundle(self, cntx, name, path, update_existence=True):

        bundle_item = f'{cntx}/{name}_ubndl'
        if ix.item_exists(bundle_item) and update_existence:
            bundle_item = ix.get_item(bundle_item)
        else:
            bundle_item = ix.cmds.CreateObject(name + "_ubndl", "GeometryBundleUsd", "Global", str(cntx))

        if not bundle_item:
            raise "Can not load asset as a abc bundle"
        ix.cmds.SetUsdBundleFilename([str(bundle_item) + ".filename[0]"], [str(path)], [0])
        return bundle_item

    @error(name=__name__)
    def import_geo(self, geo_path, asset_name=None, context="build://project", geo_type='Alembic Bundle',
                   update_existence=True):
        geo_path = unquote(geo_path)

        _types = {
            'Alembic Reference': self.create_ref,
            'USD Reference': self.create_ref,
            'Alembic Bundle': self.abc_bundle,
            'USD Bundle': self.usd_bundle
        }

        geo_cntx = self.create_context(context)
        if asset_name is None:
            asset_name = os.path.basename(geo_path).rsplit('.', 1)[-1]

        geo_item = _types[geo_type](geo_cntx, asset_name, geo_path, update_existence)

        ix.application.check_for_events()

        # create combiner
        # cmbr = self.create_node(asset_name + "_geo", "SceneObjectCombiner", str(geo_cntx))
        # ix.cmds.AddValues([str(cmbr) + ".objects"], [geo_item])

        # set scale

        ix.application.check_for_events()

        return geo_item

    @error(name=__name__)
    def import_texture(self, tex_path, cntx, udim=None, colorspace='aces', color=False):
        """
        To import the texture inside clarisse
        """

        if not os.path.isfile(tex_path):
            ix.log_warning(f'System Error: Can not import "{tex_path}" file. It not located.')
            # return False
        tex_name = os.path.basename(tex_path).split('.')[0]
        tex_node = self.create_node(tex_name, 'TextureStreamedMapFile', cntx)

        # Check UDIM
        if udim:
            tex_path = re.sub(r'_\d+\.', '_<UDIM>.', tex_path)
            tex_path = re.sub(r'\.\d+\.', '.<UDIM>.', tex_path)

        if not tex_node:
            tex_node = ix.get_item(str(cntx) + "/" + tex_name)

        tex_node.attrs.filename = str(tex_path)

        tex_node.attrs.color_space_auto_detect[0] = False
        tex_node.attrs.use_raw_data[0] = 0
        self.set_colorspace(tex_node, colorspace=colorspace, color=color)

        return tex_node

    def set_colorspace(self, node, colorspace='aces', color=False):
        """
        To set the colorspace to node
        :param node:
        :return:
        """
        if not node:
            return
        tex_path = node.attrs.filename[0]

        hdr = get_textures_settings('hdr_extension')
        extension = tex_path.rsplit('.', 1)[-1]
        if colorspace == 'aces':
            if color:
                if extension in hdr:
                    cs_config = 'aces_color_hdr'
                else:
                    cs_config = 'aces_color_sdr'
            else:
                cs_config = 'aces_raw'
        else:
            if color:
                cs_config = 'srgb'
            else:
                cs_config = 'raw'

        colorspace_value = get_colorspace_settings(cs_config)
        node.attrs.file_color_space[0] = colorspace_value

    def get_shading_group(self, bundle):
        """
        To get the shading groups of bundle
        :param bundle: clarisse item object
        :return: (dict) sg name with them indces
        """

        sgs = {}
        module = ix.get_item(str(bundle)).get_module()
        for i in range(module.get_shading_group_count()):
            shape = module.get_shading_group(i)
            sgs[str(shape)] = i

        return sgs

    def get_selected_context(self):
        selection = ix.selection
        if selection:
            if not selection[0].is_context():
                ctx = os.path.dirname(str(selection[0]))
            else:
                ctx = str(selection[0])
            return ctx
        else:
            ix.log_warning('Make sure the selection is a context')

    @error(name=__name__)
    def import_asset(self, asset, colorspace='aces'):
        self.set_material_type()

        asset_name = asset["name"]
        geos = asset["geos"]
        mtls = asset["mtls"]

        abc_file = geos.get('abc_file')

        material_attrs = get_shading_nodes('clarisse', self.material_type)

        # create contexts
        mtl_ctx = get_dcc_cfg('clarisse', 'configuration', 'material_root')
        tex_ctx = get_dcc_cfg('clarisse', 'configuration', 'texture_root')
        utils_ctx = get_dcc_cfg('clarisse', 'configuration', 'utils_root')

        # root
        root_ctx = get_dcc_cfg('clarisse', 'configuration', 'asset_root')
        root_ctx = root_ctx.replace("$assetName", asset_name)

        if ix.item_exists(root_ctx):
            ix.ix.log_error(f"[Djed] Asset already exists at: '{root_ctx}'")
            return

        root_ctx = self.create_context(root_ctx)

        geo_ctx = self.create_context(root_ctx + "/geo/abc")
        mtl_ctx = self.create_context(mtl_ctx.replace('..', root_ctx))
        tex_ctx = self.create_context(tex_ctx.replace('..', root_ctx))
        utils_ctx = self.create_context(utils_ctx.replace('..', root_ctx))

        # import geos
        mesh_data = self.import_geo(abc_file, name=asset_name, context=str(geo_ctx))

        abc_bundle = mesh_data.get("abc_bundle")

        # shape path from bundle
        sgs = self.get_shading_group(abc_bundle)

        # shape path from reference
        mtls_with_shapes = mesh_data.get("mtls")

        created_mtls = []
        for mtl in mtls:
            mtl_node = self.create_node(mtl, self.material_type, cntx=mtl_ctx)
            created_mtls.append((mtl_node, str(mtl_node).rsplit("/", 1)[-1]))
            for map_type in mtls.get(mtl):
                # get asset data
                textures = mtls.get(mtl, {}).get(map_type, {})
                texture_path = textures.get("texture_path", "")
                udim_num = textures.get("udim_num", 0)
                res = textures.get("res", "")
                map_dtype = textures.get("type", "")

                # create texture
                file_node = self.import_texture(texture_path, tex_ctx, udim=udim_num, colorspace=colorspace,
                                                color=map_dtype == 'color')
                attr = material_attrs.get(map_type, "")
                if not attr:
                    continue

                tex_attr = mtl_node.get_attribute(attr)
                if map_type == 'normal':
                    ix.cmds.SetTexture([str(tex_attr)], str(file_node))
                    normal_name = mtl + '_normal'
                    normal_node = self.create_node(normal_name, material_type='TextureNormalMap', cntx=utils_ctx)
                    if not normal_node:
                        normal_node = ix.get_item(str(utils_ctx) + "/" + normal_name)
                    ix.cmds.SetTexture([str(normal_node) + '.input'], str(file_node))
                    ix.cmds.SetTexture([str(tex_attr)], str(normal_node))
                    continue

                if map_type == 'height':
                    continue
                    disp_name = mtl + '_displacement'
                    displace_node = self.create_node(disp_name, material_type='Displacement', cntx=mtl_cntx)
                    if not displace_node:
                        displace_node = ix.get_item(str(mtl_cntx) + "/" + disp_name)

                    displace_node.attrs.front_value = str(file_node)

                    for shape in shapes:
                        shape.attrs.displacements[0] = str(displace_node)

                ix.cmds.SetTexture([str(tex_attr)], str(file_node))

        # assign materials
        for mtl_node, mtl_name in created_mtls:
            for mtl in mtls_with_shapes:
                if re.search(mtl + r"[\d+]*$", mtl_name):
                    shapes = [x[1] for x in mtls_with_shapes.get(mtl)]
                    # shape path from bundle
                    for sg in sgs:
                        index = sgs.get(sg)
                        for shape in shapes:
                            if re.search(shape, sg):
                                ix.cmds.SetValues([str(abc_bundle) + f".materials[{index}]"], [str(mtl_node)])


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
