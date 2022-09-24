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

sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.file_manager import FileManager
from utils.decorators import error


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
        node_path = ix.item_exists(cntx_path + '/' + name)
        if not node_path:
            node_path = ix.cmds.CreateObject(str(name), material_type, 'Global', str(cntx_path))
            return node_path
        else:
            return False

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

    def geo_type(self, geo_type):
        if geo_type == "Alembic Reference":
            self.working_geo_type = "abc_ref"
        else:
            self.working_geo_type = "abc_ref"

    @error(name=__name__)
    def import_geo(self, geo_path, name=None, context="build://project", geo_type='abc_ref', update_existence=True):
        mesh_path = unquote(geo_path)

        geo_cntx = self.create_context(context)
        if name is None:
            name = os.path.basename(mesh_path).rsplit('.', 1)[-1]

        # create abc reference
        abc_ref_cntx = ix.cmds.CreateCustomContext(name + "_abc_ref", "Reference", "", str(geo_cntx))
        ix.cmds.SetReferenceFilenames([ix.get_item(str(abc_ref_cntx))], [1, 0], [mesh_path])
        # abc_ref_cntx = ix.cmds.CreateFileReference(str(geo_cntx), [mesh_path])

        ix.application.check_for_events()

        # create abc bunble
        abc_bundle_cntx = ix.cmds.CreateObject(name + "_abc_bndl", "GeometryBundleAlembic", "Global", str(geo_cntx))
        ix.cmds.SetValues([str(abc_bundle_cntx) + ".filename[0]"], [str(mesh_path)])

        # create combiner
        abc_cmb = self.create_node(name + "_abc_geo", "SceneObjectCombiner", str(geo_cntx))
        ix.cmds.AddValues([str(abc_cmb) + ".objects"], [abc_bundle_cntx])

        # set scale

        ix.application.check_for_events()

        # get shapes
        shapes = self.get_objects_by_type('GeometryAbcMesh', str(abc_ref_cntx))
        mesh_data = {"abc_ref": str(abc_ref_cntx), "abc_bundle": str(abc_bundle_cntx), "mtls": {}}
        for shape in shapes:
            path = str(shape).replace(str(abc_ref_cntx), "")
            mtls = self.get_property(shape, 'materialBinding')
            if not mtls:
                continue
            mtls = mtls.split(';')
            for mtl in mtls:
                if mtl not in mesh_data["mtls"]:
                    mesh_data["mtls"][mtl] = []
                mesh_data["mtls"][mtl].append((shape, path))

        # disable the reference
        ix.cmds.DisableItems([str(abc_ref_cntx)], True)
        return mesh_data

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
            tex_path = re.sub('\.\d+\.', '.<UDIM>.', tex_path)

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

        hdr = self.fm.get_cfg("hdr")
        extension = tex_path.rsplit('.', 1)[-1]
        if colorspace == 'aces':
            if color:
                if (extension in hdr):
                    cs_config = self.fm.get_cfg("colorspace")["aces_color_hdr"]
                else:
                    cs_config = self.fm.get_cfg("colorspace")["aces_color_ldr"]
            else:
                cs_config = self.fm.get_cfg("colorspace")["aces_raw"]
        else:
            if color:
                cs_config = self.fm.get_cfg("colorspace")["srgb"]
            else:
                cs_config = self.fm.get_cfg("colorspace")["raw"]

        node.attrs.file_color_space[0] = cs_config

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

    @error(name=__name__)
    def import_asset(self, asset, colorspace='aces'):
        self.set_material_type()

        asset_name = asset["name"]
        geos = asset["geos"]
        mtls = asset["mtls"]

        abc_file = geos.get('abc_file')

        material_attrs = self.fm.get_user_json('renderer', self.material_type)

        # create contexts
        mtl_ctx = self.fm.get_user_json('clarisse', 'material_root')
        tex_ctx = self.fm.get_user_json('clarisse', 'texture_root')
        utils_ctx = self.fm.get_user_json('clarisse', 'utils_root')

        # root
        root_ctx = self.fm.get_user_json('clarisse', 'asset_root').replace("$assetName", asset_name)
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
