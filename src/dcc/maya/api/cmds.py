# -*- coding: utf-8 -*-
"""
Documentation:
"""


import importlib
# ---------------------------------
# import libraries
import json
import math
import os
import re
import sys

# maya
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel

# QT
from PySide2.QtWidgets import QMessageBox, QWidget
from shiboken2 import wrapInstance

DJED_ROOT = os.getenv("DJED_ROOT")
scripts_path = os.path.join(DJED_ROOT, "src")

sysPaths = [DJED_ROOT, scripts_path]
for sysPath in sysPaths:
    if not sysPath in sys.path:
        sys.path.append(sysPath)


from dcc.maya.api.renderer import arnold

from utils.file_manager import FileManager
from utils.decorators import error
from utils.dialogs import message, info
from utils.assets_db import AssetsDB
from utils.open_ports import OpenSocket

# initialize database
db = AssetsDB()


def maya_main_window():
    # Return the Maya main window widget as a Python object
    main_window_ptr = omui.MQtUtil.mainWindow()
    maya_win = wrapInstance(int(main_window_ptr), QWidget)

    return maya_win


# ---------------------------------
class Maya():
    
    publish_plugins = ["AbcExport.mll", "fbxmaya.mll", "AbcImport.mll", "objExport.mll", "mayaUsdPlugin.mll"]

    def __init__(self, renderer=None):

        self.renderer = renderer
        if renderer is None:
            self.renderer = arnold

        self.main_window = maya_main_window()

        self.fm = FileManager()
        self.root = os.getenv("DJED_ROOT")

        self.startup()

    @error(name=__name__)
    def startup(self):
        self.renameDuplicates()
        self.load_all_plugins()


    @error(name=__name__)
    def load_plugin(self, plugin_name="AbcExport.mll"):
        if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
            cmds.loadPlugin(plugin_name)


    @error(name=__name__)
    def load_all_plugins(self):
        for plugin in self.publish_plugins:
            try:
                self.load_plugin(plugin)
            except:
                pass

    @error(name=__name__)
    def convert_path(self, path):
        file_path = self.get_file_path()
        if not file_path:
            return
        export_dir = path
        if path.startswith(".."):
            export_dir = file_path

            for i in range(path.count("../")):
                export_dir = os.path.dirname(export_dir)

            if "../" in path:
                export_dir = os.path.join(export_dir, path.rsplit("../", 1)[-1])

        selection = self.selection()
        if selection:
            selection = selection[0]
            if not cmds.nodeType(selection) == "transform":
                message(None, "Waring", "You should select at least one valid object")

        selection = self.selection()
        export_dir = export_dir.replace("$selection", self.selection()[0])
        return export_dir.replace("\\", "/")

    @error(name=__name__)
    def get_export_path(self):
        export_root = self.fm.get_cfg("maya").get("export_root")
        return self.convert_path(export_root)

    @error(name=__name__)
    def get_project_name(self):
        project_dir = self.get_project_dir()
        if os.path.isdir(project_dir):
            return project_dir.split("/")[-2]

    @error(name=__name__)
    def get_project_dir(self):
        return cmds.workspace(q=1, rd=1)

    @error(name=__name__)
    def get_file_path(self):
        file_path = cmds.file(q=1, sn=1)
        if file_path:
            return file_path
        else:
            message(None, "Error", "You must save the file first.")

    def get_file_dir(self):
        if self.get_file_path():
            return os.path.dirname(self.get_file_path())

    @error(name=__name__)
    def get_file_name(self):
        if self.get_file_path():
            return os.path.basename(self.get_file_path())

    @error(name=__name__)
    def selection(self):
        selection = cmds.ls(sl=1)
        if selection:
            return selection
        else:
            QMessageBox(None, "Error", "Make sure you select any object.")

        return []

    @error(name=__name__)
    def current_frame(self):
        return cmds.currentTime(q=True)

    @error(name=__name__)
    def materials(self):
        self.vaildate_renderer()
        material_type = self.renderer.material_type
        return cmds.ls(sl=1, type=material_type)

    @error(name=__name__)
    def get_renderer(self):
        """
        To get the renderer name
        :return:
        """
        return cmds.getAttr('defaultRenderGlobals.currentRenderer')

    @error(__name__)
    def deleteUnsedNodes(self):
        """
        To delete unused nodes in hypershade
        """
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        mel.eval('MLdeleteUnused;')

    @error(__name__)
    def arrangeHypershade(self):
        mel.eval('HypershadeWindow;')
        mel.eval('hyperShadePanelGraphCommand("hyperShadePanel1", "rearrangeGraph");')

    @error(__name__)
    def closeHypershade(self):
        mel.eval('deleteUI hyperShadePanel1Window;')

    @error(name=__name__)
    def vaildate_renderer(self):
        material_type = self.renderer.material_type
        if not self.renderer.name == self.get_renderer():
            raise (f"Set the current renderer to {self.renderer.name} frist")

    @error(__name__)
    def create_material(self, name="materialMTL#", sg=None):
        """
        To creates material with given type
        :param name: (str) the name of material
        :return:(list(str)) material name
        """
        self.vaildate_renderer()
        material_type = self.renderer.material_type
        name = re.sub(r"(?i)sg$", "MTL", name)
        mat = cmds.shadingNode(material_type, name=name, asShader=True)

        if sg:
            if not cmds.objExists(sg):
                sg = cmds.sets(empty=1, renderable=1, noSurfaceShader=1, n=sg)
        else:
            sg = cmds.sets(empty=1, renderable=1, noSurfaceShader=1, n=re.sub(r"(?i)mtl$", "SG", name))

        cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", f=1)

        return mat, sg

    @error(__name__)
    def assign_material(self, objects, mtl_name=None, sg_name=None):
        """
        TO assign materials to objects by given material name or shading group name
        :param objects: (list) list of objetcs names
        :param mtl_name: (str) the material name
        :param sg_name: (str) the shading group name
        :return:(bool) the status of assignment
        """
        if sg_name:
            cmds.sets(objects, e=True, forceElement=sg_name)
            return True

        if mtl_name:
            sg_name = cmds.listConnections(mtl_name, d=1, s=0, type="shadingEngine")[0]
            cmds.sets(objects, e=True, forceElement=sg_name)

            return True

    @error(__name__)
    def import_texture(self, tex_path, udim=None, colorspace='aces', color=False):
        """
        To import the texture inside maya
        """
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

        if not os.path.isfile(tex_path):
            cmds.warning("System Error: Can not import {} file. It not located.")
            return False
        tex_name = os.path.basename(tex_path).split(".")[0]

        if not cmds.objExists(tex_name):
            place2d = cmds.shadingNode("place2dTexture", asUtility=True, n="p2d_#")
            file_node = cmds.shadingNode("file", asTexture=True, n=tex_name)
            cmds.defaultNavigation(connectToExisting=True, source=place2d, force=True, destination=file_node)
        else:
            file_node = tex_name

        cmds.setAttr(file_node + ".fileTextureName", tex_path, type="string")

        cmds.setAttr(file_node + ".aiAutoTx", 0)

        # Ckeck UDIM
        if self.fm.ck_udim(tex_path) and udim:
            cmds.setAttr(file_node + ".uvTilingMode", 3)

        # colorspace
        cmds.setAttr(file_node + ".colorSpace", cs_config, type="string")

        # texture preview
        if color:
            mel.eval(f'generateUvTilePreview {file_node};')

        return tex_name

    @error(name=__name__)
    def create_material_with_texture(self, directory: str, material_type=None, colorspace="aces", sg_mtl=None,
                                     ckSG=True):
        hdr = self.fm.get_cfg("hdr")
        if colorspace == "aces":
            cs_h = self.fm.get_cfg("colorspace")["aces_color_hdr"]
            cs_l = self.fm.get_cfg("colorspace")["aces_color_ldr"]
            cs_r = self.fm.get_cfg("colorspace")["aces_raw"]
        else:
            cs_h = self.fm.get_cfg("colorspace")["srgb"]
            cs_r = self.fm.get_cfg("colorspace")["raw"]

        # mtl_attr = self.fm.get_cfg(self.renderer.name())
        mtl_attr = self.fm.get_cfg('renderer')['arnold']

        textures = self.fm.list_images(directory)

        if material_type is not None:
            mtl_name, sg_name = self.create_material(material_type)
        else:
            mtl_name, sg_name = sg_mtl

        for tex in textures:
            tex_path = os.path.join(directory, tex)

            if not (ckSG and (sg_name in tex_path)):
                continue

            # check udim
            if self.fm.ck_udim(tex_path):
                if not re.search(r"\.1001\.", tex_path):
                    continue
            # import textures
            file_node = self.import_texture(tex_path)

            # colorspace
            cmds.setAttr(file_node + ".colorSpace", cs_r, type="string")

            # Ckeck Texture Type
            tex_type = self.fm.ck_tex(tex)
            mtl_plug = mtl_name + mtl_attr[tex_type]

            if tex_type == "basecolor":
                cmds.connectAttr(file_node + ".outColor", mtl_plug, f=1)

                if colorspace == "aces":
                    if tex.split(".")[-1] in hdr:
                        cmds.setAttr(file_node + ".colorSpace", cs_h, type="string")
                    else:
                        cmds.setAttr(file_node + ".colorSpace", cs_l, type="string")
                else:
                    cmds.setAttr(file_node + ".colorSpace", cs_h, type="string")

            if tex_type == "roughness":
                cmds.connectAttr(file_node + ".outColor.outColorR", mtl_plug, f=1)
                cmds.setAttr(file_node + ".alphaIsLuminance", 1)

            if tex_type == "metallic":
                cmds.connectAttr(file_node + ".outColor.outColorR", mtl_plug, f=1)
                cmds.setAttr(file_node + ".alphaIsLuminance", 1)

            if tex_type == "opacity":
                cmds.connectAttr(file_node + ".outColor.outColorR", mtl_plug, f=1)
                cmds.setAttr(file_node + ".alphaIsLuminance", 1)

            if tex_type == "sss":
                cmds.connectAttr(file_node + ".outColor.outColorR", mtl_plug, f=1)
                cmds.setAttr(file_node + ".alphaIsLuminance", 1)

            if tex_type == "normal":
                normal_name = file_node + '_normMap'
                cmds.setAttr(file_node + ".alphaIsLuminance", 0)
                if not cmds.objExists(normal_name):
                    normal_map = cmds.shadingNode('aiNormalMap', n=normal_name, asUtility=1)
                else:
                    normal_map = normal_name
                cmds.connectAttr(file_node + '.outColor', normal_map + '.input', f=1)
                cmds.connectAttr(normal_map + '.outValue', mtl_plug, f=1)

            if tex_type == "height":
                disp_name = file_node + '_displcShd'
                if not cmds.objExists(disp_name):
                    disp_mtl = cmds.shadingNode('displacementShader', n=disp_name, asShader=1)
                else:
                    disp_mtl = disp_name
                cmds.connectAttr(file_node + '.outColor.outColorR', disp_mtl + '.displacement', f=1)
                cmds.connectAttr(disp_mtl + '.displacement', sg_name + mtl_attr[tex_type], f=1)

        self.arrangeHypershade()

    @error(name=__name__)
    def create_material_with_texture(self, asset: dict, colorspace="aces"):
        '''
        To create material linked with textures (uber material) from the dictionary
        :param asset :(dict) asset dictionary
        :param colorspace :(str) the colorspace of textures
        :return: (list) list of created shadingGroup
        '''

        asset_name = asset["name"]
        geos = asset["geos"]
        mtls = asset["mtls"]

        renderer_name = self.renderer.name

        sgs = []

        mtl_attr = self.fm.get_cfg('renderer')[renderer_name]
        for sg in mtls:
            # create material
            mtl_name, sg_name = self.create_material(name=sg)
            sgs.append(sg_name)

            for map_type_name in mtls.get(sg, {}):
                textures = mtls.get(sg, {}).get(map_type_name, {})
                texture_path = textures.get("texture_path", "")
                udim_num = textures.get("udim_num", 0)
                res = textures.get("res", "")
                map_dtype = textures.get("type", "")

                # create texture
                file_node = self.import_texture(texture_path, udim_num, colorspace=colorspace, color=map_dtype == 'color')
                mtl_plug = mtl_name + mtl_attr[map_type_name]

                if map_type_name == "normal":
                    normal_name = file_node + '_normMap'
                    cmds.setAttr(file_node + ".alphaIsLuminance", 0)
                    normal_map = cmds.shadingNode('aiNormalMap', n=normal_name, asUtility=1)
                    cmds.connectAttr(file_node + '.outColor', normal_map + '.input', f=1)
                    cmds.connectAttr(normal_map + '.outValue', mtl_plug, f=1)
                    continue

                elif map_type_name == "height":
                    disp_name = file_node + '_displcShd'
                    disp_mtl = cmds.shadingNode('displacementShader', n=disp_name, asShader=1)
                    cmds.connectAttr(file_node + '.outColor.outColorR', disp_mtl + '.displacement', f=1)
                    cmds.connectAttr(disp_mtl + '.displacement', sg_name + mtl_attr[map_type_name], f=1)
                    continue

                mtl_plug = mtl_name + mtl_attr[map_type_name]

                if map_dtype == "float":
                    tex_plug = file_node + ".outColor.outColorR"
                else:
                    tex_plug = file_node + ".outColor"

                cmds.connectAttr(tex_plug, mtl_plug, f=1)
        self.arrangeHypershade()
        return sgs

    @error(name=__name__)
    def get_asset_data(self, node):
        """
        To gather all selection data meshes, attributes, materials, textures,
        :param node: Transform node of asset
        :return:
        """

        data = {}
        # Get all selection shapes
        shapes = self.list_all_dag_meshes(node, shape=True, fullPath=True, type=om.MFn.kMesh)
        for shapeNode in shapes:
            # Get each shape shadingEngine
            sgs = cmds.listConnections(shapeNode, s=0, d=1, type="shadingEngine")
            if not sgs:
                continue
            for sg in sgs:
                if (sg in data) or (sg == 'initialShadingGroup'):
                    continue

                data[sg] = {
                    "materials": {},
                    "displacements": {},
                    "meshes": {}
                }
                # list of meshes
                meshes = self.list_all_DG_nodes(sg, om.MFn.kMesh, om.MItDependencyGraph.kUpstream)
                data[sg]["meshes"]["shape"] = meshes

                # Get displacement
                displacements = self.get_materials_from_sg(sg, "displacement")
                attrs = {}
                if displacements:
                    displace = displacements[0]
                    _type = cmds.nodeType(displace)
                    tex = self.get_texs_from_mtl(displace, {"displacementShader": ""})
                else:
                    # if there is map connected directly in shading group
                    displace = "displacement_"
                    _type = "displacementShader"
                    tex = self.get_texs_from_mtl(sg, {"displacement": ""})
                    # if not tex:
                    #     # if there is map connected directly in shading group
                    #     tex = self.get_texs_from_mtl(sg, {"displacement": ""})
                if tex:
                    data[sg]["displacements"][displace] = {}
                    data[sg]["displacements"][displace]["type"] = _type
                    data[sg]["displacements"][displace]["texs"] = tex
                    data[sg]["displacements"][displace]["attrs"] = attrs

                # Get materials
                mtls = self.get_materials_from_sg(sg)
                for mtl in mtls:
                    data[sg]["materials"][mtl] = {}
                    data[sg]["materials"][mtl]["type"] = cmds.nodeType(mtl)
                    attrs = {}
                    for attr, value in self.get_attrs(mtl, default_values=False).items():
                        attrs[attr] = value

                    texs = self.get_texs_from_mtl(mtl)
                    data[sg]["materials"][mtl]["attrs"] = attrs
                    data[sg]["materials"][mtl]["texs"] = texs

        return data


    @error(name=__name__)
    def export_selection(self, asset_dir=None, asset_name=None, export_type=["abc"], _message=True):

        """
        To export the selection
        :param asset_name: the asset name if None it will get the name of selection
        :param asset_dir: the base directory to export asset
        :param _message: popup message
        :param export_type: list(str): list of export types
        :return:
        """

        # get asset name
        if asset_name is None:
            selection = self.selection()
            if not selection:
                message(None, "waring", "you should select at last one object")
                return
            if not (cmds.nodeType(selection[0]) == "transform"):
                return
            asset_name = selection[0]

        if asset_dir is None:
            export_dir = self.get_export_path()
        else:
            export_dir = self.convert_path(asset_dir)

        if not export_dir:
            return
        self.fm.make_dirs(export_dir)
        export_path = self.fm.version_up(export_dir, prefix=asset_name + "_v")

        self.fm.make_dirs(os.path.dirname(export_path))

        # add mtl attribute
        attr_name = "materialBinding"
        self.add_attr_to_shapes([asset_name], attr_name)

        db.add_asset(asset_name=asset_name)
        db.add_geometry(asset_name=asset_name, source_file=self.get_file_path())

        export_paths = {}
        for ext in export_type:
            if ext == "obj":
                db.add_geometry(asset_name=asset_name, obj_file=export_path + "." + ext)
                cmds.file(export_path, es=1, f=1, typ="OBJexport",
                          options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
                export_paths[ext] = export_path + "." + ext

            elif ext == "fbx":
                db.add_geometry(asset_name=asset_name, fbx_file=export_path + "." + ext)
                cmds.file(export_path, es=1, f=1, typ="FBX export",
                          options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
                export_paths[ext] = export_path + "." + ext

            elif ext == "abc":
                db.add_geometry(asset_name=asset_name, abc_file=export_path + "." + ext)
                frameRange = (self.current_frame(), self.current_frame())
                abcOptions = f" -attr {attr_name} -uvWrite -writeFaceSets -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa"
                root = " -root " + " -root ".join([asset_name])
                command = "-frameRange " + str(frameRange[0]) + " " + str(
                    frameRange[1]) + abcOptions + root + " -file " + export_path + ".abc"
                cmds.AbcExport(j=command, verbose=1)
                export_paths[ext] = export_path + "." + ext

            elif ext == "usd":
                options = ";"
                options += "exportUVs=1;"
                options += "exportSkels=none;"
                options += "exportSkin=none;"
                options += "exportBlendShapes=0;"
                options += "exportColorSets=1;"
                options += "defaultMeshScheme=none;"
                options += "defaultUSDFormat=usdc;"
                options += "animation=0;"
                options += "eulerFilter=0;"
                options += "staticSingleSample=0;"
                options += "startTime={};".format(self.current_frame())
                options += "endTime={};".format(self.current_frame())
                options += "frameStride=1;"
                options += "frameSample=0.0"
                options += "parentScope=;"
                options += "exportDisplayColor=0;"
                options += "shadingMode=none;"
                options += "exportInstances=1;"
                options += "exportVisibility=1;"
                options += "mergeTransformAndShape=1;"
                options += "stripNamespaces=0"

                db.add_geometry(asset_name=asset_name, usd_geo_file=export_path + "." + ext)
                cmds.file(export_path, es=1, f=1, typ="USD Export", options=options)
                export_paths[ext] = export_path + "." + ext


            else:
                return

            print("[Geometry Exported]: ", export_path + "." + ext)
        if _message:
            info(None, "'{}' exported successfully with formats '{}'".format(asset_name, export_type))

        # maya_file_path = self.get_file_path()
        # if maya_file_path:
        #     self.fm.set_user_json(last_object_path=export_paths,
        #                           last_maya_path=maya_file_path
        #                           )
            return export_paths

    @error(name=__name__)
    def import_geo(self, geo_path):
        '''
        To import geometry into maya scene
        :param geo_path: the geo path with different geo extensions
        :return: the imported root nodes
        '''
        before = cmds.ls(assemblies=1)
        if geo_path.endswith(".abc"):
            cmds.AbcImport(geo_path)
        else:
            cmds.file(geo_path, i=1)
        after = cmds.ls(assemblies=1)
        imported_nodes = list(set(after) - set(before))
        return imported_nodes

    @error(name=__name__)
    def add_attribute(self, geo, attr_name):
        try:
            cmds.getAttr(geo + "." + attr_name)
        except:
            cmds.addAttr(geo, longName=attr_name, dataType='string', keyable=1)

    @error(name=__name__)
    def add_attr_to_shapes(self, objects, attr_name):
        for object in objects:
            for shape in self.list_all_dag_meshes(object, om.MFn.kMesh):
                sgs = self.list_all_DG_nodes(shape, om.MFn.kShadingEngine)
                self.add_attribute(shape, attr_name)
                cmds.setAttr(shape + "." + attr_name, ";".join(sgs), type="string")

    @error(name=__name__)
    def list_all_DG_nodes(self, inNode, node_type=om.MFn.kShadingEngine, direction=om.MItDependencyGraph.kDownstream):
        """
        To get the all connection nodes by type
        direction : om.MItDependencyGraph.kUpstream
        nodeMfnType : om.MFn.kShadingEngine, om.MFn.kMesh, om.MFn.kFileTexture

        ## Test ##
        for i in getAllDGNodes("SHoes_PartsShape4", om.MFn.kShadingEngine, om.MItDependencyGraph.kDownstream):
        print(getAllDGNodes(i, om.MFn.kMesh, om.MItDependencyGraph.kUpstream))

        """

        nodes = []
        # Create a MSelectionList to add the object:
        selection_list = om.MSelectionList()
        selection_list.add(inNode)
        mObject = selection_list.getDependNode(0)  # The current object
        node_fn = om.MFnDagNode(mObject)

        # Create a dependency graph iterator for the current object:
        mItDependencyGraph = om.MItDependencyGraph(mObject, direction, direction)
        while not mItDependencyGraph.isDone():
            currentNode = mItDependencyGraph.currentNode()
            dependNode_fn = om.MFnDependencyNode(currentNode)

            # print("Current Node: ", dependNodeFunc.name())
            # Check the type of node
            if currentNode.hasFn(node_type):
                name = dependNode_fn.name()

                if currentNode.hasFn(om.MFn.kDagNode):
                    dagNode_fn = om.MFnDagNode(currentNode)
                    name = dagNode_fn.fullPathName()
                nodes.append(name)
            mItDependencyGraph.next()

        return nodes

    @error(name=__name__)
    def ck_parents_vis(self, nodeFn):
        """
        check if one of node parent is hidden
        :param:(MFnDagNode)
        :return: True if all parent are shown, False if any parebt is hidden
        """
        for i in range(nodeFn.parentCount()):
            parent_obj = nodeFn.parent(i)
            parent_fn = om.MFnDagNode(parent_obj)
            plug = nodeFn.findPlug("visibility", False)
            if plug.asBool():  # if visibility on
                if not self.ck_parents_vis(parent_fn):
                    return False
            else:
                return False
        return True

    @error(name=__name__)
    def list_all_dag_meshes(self, node=None, shape=True, fullPath=True, type=om.MFn.kMesh, hidden=False):
        """
        list all objects in children by type on selection
        :param shape: return shapes
        :param fullPath:
        :param type: MFn Type
        :param hidden: include hidden objects or not, True: included
        :return: list of objects names
        """

        traversal_type = om.MItDag.kDepthFirst
        filter_type = type

        objectsList = []
        if node is None:
            selection_list = om.MGlobal.getActiveSelectionList()
        else:
            selection_list = om.MSelectionList()
            selection_list.add(node)

        # dag iterator
        dag_iter = om.MItDag(traversal_type, filter_type)

        for i in range(selection_list.length()):
            if not (selection_list.isEmpty() and dag_iter.isDone()):
                dag_iter.reset(selection_list.getDependNode(i), traversal_type, filter_type)

            while not dag_iter.isDone():
                # MObject
                shape_obj = dag_iter.currentItem()
                # DagNode
                shape_fn = om.MFnDagNode(shape_obj)
                # check intermediate
                inter_plug = shape_fn.findPlug("intermediateObject", False)
                # check if node is not intermediate and not hidden in viewport
                if (hidden or self.ck_parents_vis(shape_fn)) and (not inter_plug.asBool()):
                    if shape:
                        if fullPath:
                            objectsList.append(shape_fn.fullPathName())
                        else:
                            objectsList.append(shape_fn.name())
                    else:
                        parent_fn = om.MFnDagNode(shape_fn.parent(0))

                        if fullPath:
                            objectsList.append(parent_fn.fullPathName())
                        else:
                            objectsList.append(parent_fn.name())
                dag_iter.next()
        return objectsList

    @error(name=__name__)
    def get_materials_from_sg(self, sgName, _type="material"):
        """
        To get the materials names from the shading group name
        @param sgName: (str) shading group name
        @return: (list(str)) list of material names
        """

        if _type == "material":
            satisfy = "shader/surface"
        else:
            satisfy = "shader/displacement"

        inConnection = cmds.listConnections(sgName, s=1, d=0)

        mtls = []
        for node in inConnection:
            if cmds.getClassification(cmds.nodeType(node), sat=satisfy):
                mtls.append(node)

        return mtls

    def get_attrs(self, node_name, default_values=False, connected=False):
        """
        To get the attributes that have default values or not have default values base on default_attr value
        :param node_name: (str) the node name
        :param default_values: (bool) return the attrs that have default values
        :param connected: (bool) return the connected attributes
        :return: dict of attrs with its values
        """

        attrs = {}
        mtl_selectionList = om.MSelectionList()
        mtl_selectionList.add(node_name)
        mtl_mObject = mtl_selectionList.getDependNode(0)

        mtl_fn = om.MFnDependencyNode(mtl_mObject)

        for i in range(mtl_fn.attributeCount()):
            m_attr = mtl_fn.attribute(i)
            attr_fn = om.MFnAttribute(m_attr)
            plug = mtl_fn.findPlug(m_attr, False)

            if connected and plug.isDestination:
                attrs[attr_fn.name] = ''
            else:
                if attr_fn.storable and attr_fn.connectable and (not plug.isChild):
                    if default_values and plug.isDefaultValue():
                        if plug.isDefaultValue():
                            attrs[attr_fn.name] = cmds.getAttr(plug.name())
                    else:
                        if not plug.isDefaultValue():
                            attrs[attr_fn.name] = cmds.getAttr(plug.name())
        return attrs



    @error(name=__name__)
    def get_texs_from_mtl(self, mtlNode, mtl_data=None):
        """
        To get the nodes that finally plugs in material node.
        :param mtlNode:(str) the material node name
        :param mtl_data (dict) the material plugs data
        :return: dict of node info
        {
        <fileNodeName>:
            {"filepath": str,
             "colorspace": str,
             "plugs": list
            }
        }
        """
        # Getting the file textures nodes
        text_fileNodes = []
        re_objects = True
        type_file = om.MFn.kFileTexture
        search_direction = om.MItDependencyGraph.kUpstream


        if mtl_data is None:
            output_files = self.get_attrs(mtlNode, connected=True)
        else:
            output_files = list(mtl_data.keys())


        mtl_selectionList = om.MSelectionList()
        mtl_selectionList.add(mtlNode)
        mtl_mObject = mtl_selectionList.getDependNode(0)  # The current mtl object

        # Create a dependency graph iterator for the current object:
        mtl_mIt = om.MItDependencyGraph(mtl_mObject, search_direction, search_direction)

        while not mtl_mIt.isDone():
            current_network_node = mtl_mIt.currentNode()
            current_network_fn = om.MFnDependencyNode(current_network_node)

            if current_network_node.hasFn(type_file):

                if re_objects:
                    text_fileNodes.append(current_network_node)
                else:
                    node_name = current_network_fn.name()
                    text_fileNodes.append(node_name)
            mtl_mIt.next()

        fileTexture_data_dict = {}

        # Get file nodes plugs
        for tex_node in text_fileNodes:
            tex_node_dict = {"plugs": [], "filepath": None, "colorspace": None, "type": None}

            tex_fn = om.MFnDependencyNode(tex_node)
            file_path = tex_fn.findPlug("fileTextureName", False).asString().replace("<UDIM>", "1001")
            colorspace = tex_fn.findPlug("colorSpace", False).asString()

            tex_node_dict["type"] = cmds.nodeType(tex_fn.name())

            tex_node_dict["filepath"] = file_path
            tex_node_dict["colorspace"] = colorspace

            mItDependencyGraph = om.MItDependencyGraph(tex_node, om.MItDependencyGraph.kDownstream,
                                                       om.MItDependencyGraph.kDepthFirst)
            while not mItDependencyGraph.isDone():

                current_node = mItDependencyGraph.currentNode()
                current_fn = om.MFnDependencyNode(current_node)
                # print("Node: ", current_fn.name())
                for conn in current_fn.getConnections():
                    # print("connection: ", conn)
                    destins_plugs = conn.destinations()

                    for destins_plug in destins_plugs:
                        # print("destination: ", destins_plug)
                        if destins_plug:
                            plug_name = destins_plug.name()
                            # print("plug: ", plug_name)
                            attr = plug_name.split(".")[1]
                            # print("attribute: ", attr, attr in output_files)
                            if attr in output_files:
                                # print("attribute: ", attr)
                                if attr not in tex_node_dict["plugs"]:
                                    tex_node_dict["plugs"].append(attr)

                                fileTexture_data_dict[tex_fn.name()] = tex_node_dict
                mItDependencyGraph.next()

        return fileTexture_data_dict

    def renameDuplicates(self):
        """
        To rename all DAG nodes that have the same name, by incrementing the name with 1
        @return:
        """
        # Find all objects that have the same shortname as another
        # We can identify them because they have | in the name
        duplicates = [f for f in cmds.ls() if '|' in f]
        # Sort them by hierarchy so that we don't rename a parent before a child.
        duplicates.sort(key=lambda obj: obj.count('|'), reverse=True)

        # if we have duplicates, rename them
        if duplicates:
            for name in duplicates:
                try:
                    # extract the base name
                    m = re.compile("[^|]*$").search(name)
                    shortname = m.group(0)

                    # extract the numeric suffix
                    m2 = re.compile(".*[^0-9]").match(shortname)
                    if m2:
                        stripSuffix = m2.group(0)
                    else:
                        stripSuffix = shortname

                    # rename, adding '#' as the suffix, which tells maya to find the next available number
                    newname = cmds.rename(name, (stripSuffix + "#"))
                    print("renamed {} to {}".format(name, newname))
                except Exception as e:
                    print(name, e)

            print('Renamed "{}" objects with duplicated name.'.format(duplicates))

    def get_uv_sets(self, shape_node):
        uv_sets = cmds.polyUVSet(shape_node, q=1, allUVSets=1)

        return uv_sets

    def get_uv_shells(self, shape_node):
        """
        to get the dict of uv sets with its uv shells infos
        @param shape_node:(str) the shape node name of mesh
        @return: {"map1": {0: ["..map[*]"], 1: ["..map[*]"], ...}, ..}
        """

        # get full path name of shape node
        fullPathShape = cmds.ls(shape_node, l=1)[0]

        # create selection list
        selectionList = om.MSelectionList()
        selectionList.add(shape_node)

        # get dag path and function sets
        dependNode = selectionList.getDependNode(0)
        shapeFn = om.MFnMesh(dependNode)

        # get uv sets
        # uvSets = cmds.polyUVSet(fullPathShape, q=1, allUVSets=1)
        uvSets = shapeFn.getUVSetNames()

        all_Sets = {}
        for uvset in uvSets:
            shell_num, uvShellArray = shapeFn.getUvShellsIds(uvset)
            uv_num = shapeFn.numUVs()

            uvShells = {}
            for shell_id, uv_id in zip(uvShellArray, range(uv_num)):

                if not shell_id in uvShells:
                    uvShells[shell_id] = {"uv": [], "uv_point": []}

                uvShells[shell_id]["uv"].append("{}.map[{}]".format(fullPathShape, uv_id))
                uvShells[shell_id]["uv_point"].append(shapeFn.getUV(uv_id, uvset))

            all_Sets[uvset] = uvShells

        return all_Sets

    def validate_uv_shells(self, shape_node):

        def get_uv_place(uv_point):
            uv = [math.floor(x) for x in uv_point]
            return 1001 + uv[0], 1001 + uv[0] + 10 * uv[1]

        uv_shells = self.get_uv_shells(shape_node)

        for uv_set in uv_shells:
            uv_shells = uv_shells[uv_set]

            for shell_id in uv_shells:
                uv_shell = uv_shells[shell_id]
                uvs = uv_shell["uv"]
                uv_points = uv_shell["uv_point"]

                intial_location = get_uv_place(uv_points[0])
                for i, uv_point in enumerate(uv_points):
                    if intial_location != get_uv_place(uv_points[i]):
                        shape_name = shape_node.rsplit('|', 1)[-1]
                        message = "{} has a shared uv islands with borders in {}".format(shape_name, uvs)
                        return message, uvs

        return True

    def uv_sets(self, shape_node):
        uv_sets = cmds.polyUVSet(shape_node, q=1, allUVSets=1)
        return uv_sets

    def delete_uv_set(self, shape_node, uv_set):
        cmds.polyUVSet(shape_node, d=1, uvSet=uv_set)

    def rename_uv_set(self, shape_node, uv_set='map1'):
        cmds.polyUVSet(shape_node, rename=True, uvSet=self.uv_sets(shape_node)[0], newUVSet=uv_set)

    def recalculate_normals(self, shape_node):
        cmds.polyNormalPerVertex(shape_node, unFreezeNormal=True)
        cmds.polyNormal(shape_node + ".f[:]", normalMode=2, userNormalMode=1, ch=0)
        cmds.polySetToFaceNormal(shape_node)

    def is_locked_normals(self, shape_node):
        vertex_face = cmds.polyListComponentConversion(shape_node, toVertexFace=1)

        return any(cmds.polyNormalPerVertex(vertex_face, q=1, freezNormal=1))

    def split_by_material(self, selections=None, keep_original=True):
        if selections is None:
            selections = cmds.ls(sl=1)

        if isinstance(selections, str):
            selections = [selections]

        for selection in selections:
            all_meshes = self.list_all_dag_meshes(selection)

            for mesh in all_meshes:
                # get all sgs
                sgs = cmds.listConnections(mesh, d=1, s=0, type="shadingEngine")
                sgs = list(set(sgs))

                if len(sgs) < 2:
                    continue

                transform = cmds.listRelatives(mesh, p=1)[0]

                parent = cmds.listRelatives(transform, p=1)
                if parent:
                    grp = cmds.group(em=1, p=parent[0], n=transform + "_grp")
                else:
                    grp = cmds.group(em=1, w=1, n=transform + "_grp")


                for sg in sgs:
                    # duplicate the original
                    mesh_duplicated = cmds.duplicate(mesh, n=transform + "_sep#")[0]
                    temp_set = cmds.sets(mesh_duplicated + ".f[:]", n='temp_set#')

                    selected_faces = cmds.sets(sg, int=temp_set)

                    if not selected_faces:
                        cmds.delete(mesh_duplicated)
                        #cmds.delete(temp_set)
                    else:
                        cmds.select(selected_faces, r=1)
                        cmds.select(mesh_duplicated + ".f[*]", toggle=1)
                        cmds.delete()
                        cmds.delete(temp_set)

                        cmds.parent(mesh_duplicated, grp)

                cmds.parent(transform, grp)
                cmds.select(grp, r=1)

                transform_renamed = cmds.rename(transform, transform + "__orig")
                # hide the original
                if keep_original:
                    cmds.setAttr(transform_renamed + ".visibility", 0)
                else:
                    cmds.delete(transform_renamed)

    def remove_all_namespaces(self):
        # Set root namespace
        cmds.namespace(setNamespace=':')

        # Collect all namespaces except for the Maya built ins.
        all_namespaces = [x for x in cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) if
                          x != "UI" and x != "shared"]

        if all_namespaces:
            # Sort by hierarchy, deepest first.
            all_namespaces.sort(key=len, reverse=True)
            for namespace in all_namespaces:
                # When a deep namespace is removed, it also removes the root. So check here to see if these still exist.
                if cmds.namespace(exists=namespace) is True:
                    cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

    def claenup_mesh(self, shape_node):
        cmds.polyClean(shape_node, cv=1, ce=1, cuv=1, cpm=1, ch=0)
        # cmds.delete(shape_node + ".vtx[*]")
        cmds.select(shape_node, r=1)
        mel.eval(
            'polyCleanupArgList 4 { "0","1","1","0","0","1","1","1","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };')
        cmds.delete(shape_node, ch=1)

        # cmds.makeIdentity(shape_node, a=1, n=1, r=1, s=1, t=1)


    def get_file_colorspace(self):
        return cmds.colorManagementPrefs(q=True, renderingSpaceNames=True)


    def assignMaterial(self, n="newMtl#", objects=None, new=True):
        """
        TO assign material to objects or selections and apply presets
        @param n: (str) name of created material
        @param objects: (list) the objects to assign
        @return:
        """

        if not objects:
            objects = cmds.ls(sl=1)

        mat = cmds.shadingNode(self.renderer.material_type, name=n, asShader=True)
        sg = cmds.sets(empty=1, renderable=1, noSurfaceShader=1, n=n.replace("MTL", "SG"))
        cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader")
        cmds.sets(objects, e=True, forceElement=sg)


# Main function
def main():
    pass


if __name__ == '__main__':
    
    main()
    

