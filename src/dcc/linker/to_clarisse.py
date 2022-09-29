# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# import libraries
import os
import sys
from pathlib import Path

import pyblish.api
import pyblish.util

DJED_ROOT = Path(os.getenv("DJED_ROOT"))

scripts_path = os.path.join(DJED_ROOT, "Scripts")
dcc_path = os.path.join(DJED_ROOT, "Scripts", "dcc")
clarisse_path = os.path.join(DJED_ROOT, "Scripts", "dcc", "Clarisse")
ClarissePort_path = os.path.join(clarisse_path, "ClarissePort.py")

sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.file_manager import FileManager
from utils import clarisse_net as ix

# ---------------------------------

# if not ix.application.is_command_port_active():
#     ix.application.enable_command_port()

fm = FileManager()


def process(instance):
    asset_name = instance.get('name')
    data = instance.get('data')

    colorspace = data.get("colorspace", "aces")
    sgs = data.get('data')

    port = connect()
    if not port:
        return "Can not connect with clarisse port"
    cmd = "import sys\n"
    cmd += f"with open(r'{ClarissePort_path}', 'r') as f:\n"
    cmd += f"\tscript = f.read()\n"
    cmd += f"\tsys.argv = [r'{ClarissePort_path}', {kwargs}]\n"
    cmd += f"\texec(script)\n"

    port.run(cmd)



def set_port_num(port_num=None):
    if port_num is None:
        port_num = fm.get_user_json("clarisse", "command_port")
    return port_num


def connect(ip='localhost', port_num=None):
    try:
        if port_num is None:
            port_num = fm.get_user_json("clarisse", "command_port")

        port = ix.ClarisseNet(ip, port_num)
        return port
    except Exception as e:
        print(e)
        pass
    return

    # def spp_to_clarisse(self, **kwargs):
    #     port = self.connect()
    #     if not port:
    #         return "Can not connect with clarisse port"
    #     cmd = "import sys\n"
    #     cmd += f"with open(r'{ClarissePort_path}', 'r') as f:\n"
    #     cmd += f"\tscript = f.read()\n"
    #     cmd += f"\tsys.argv = [r'{ClarissePort_path}', {kwargs}]\n"
    #     cmd += f"\texec(script)\n"
    #
    #     port.run(cmd)
    #     return "Asset send successfully."
    #
    # def maya_to_clarisse(self, mayaData, cfg=None):
    #     port = self.connect()
    #     if not port:
    #         return
    #
    #     cmd = "import sys\n"
    #     cmd += f"with open(r'{ClarissePort_path}', 'r') as f:\n"
    #     cmd += f"\tscript = f.read()\n"
    #     cmd += f"\tsys.argv = [r'{ClarissePort_path}', {mayaData}, {cfg}]\n"
    #     cmd += f"\texec(script)\n"
    #
    #     port.run(cmd)



if __name__ == '__main__':
    port = connect()

    data = {"family": "asset", "name": "tv_table", "file_color_space": ["ACES - ACEScg"], "renderer": "arnold", "host": "maya", "geo_paths": {"obj": "D:/3D/working/projects/Generic/03_Workflow/Assets/tv_table/Scenefiles/mod/Modeling/Export/tv_table/tv_table_v0044.obj", "abc": "D:/3D/working/projects/Generic/03_Workflow/Assets/tv_table/Scenefiles/mod/Modeling/Export/tv_table/tv_table_v0044.abc"}, "asset_data": {"tableSG": {"materials": {"tableMTL": {"type": "aiStandardSurface", "attrs": {"normalCamera": [[0.0, 0.0, 0.0]], "baseColor": [[0.0, 0.0, 0.0]], "specularRoughness": 0.0, "metalness": 1.0}, "texs": {}}}, "displacements": {}, "meshes": {"shape": ["|tv_table|table|pCube2|pCubeShape2", "|tv_table|table|pCube1|pCubeShape1", "|tv_table|table|pCube5|pCubeShape5", "|tv_table|table|pCube6|pCubeShape6", "|tv_table|table|pCube7|pCubeShape7"]}}, "tvAntinaSG": {"materials": {"tvAntinaMTL": {"type": "aiStandardSurface", "attrs": {}, "texs": {"tv_table_v0008_tvBodySG_Normal_1": {"plugs": ["normalCamera"], "filepath": "D:/3D/working/projects/Generic/03_Workflow/Assets/tv_table/Scenefiles/sur/Textures/v0022/tv_table_v0008_tvBodySG_Normal.1001.png", "colorspace": "ACES - ACES2065-1", "type": "file", "udim": 1}, "tv_table_v0008_tvBodySG_Roughness_1": {"plugs": ["specularRoughness"], "filepath": "D:/3D/working/projects/Generic/03_Workflow/Assets/tv_table/Scenefiles/sur/Textures/v0022/tv_table_v0008_tvBodySG_Roughness.1001.png", "colorspace": "ACES - ACES2065-1", "type": "file", "udim": 1}, "tv_table_v0008_tvBodySG_Metalness_1": {"plugs": ["metalness"], "filepath": "D:/3D/working/projects/Generic/03_Workflow/Assets/tv_table/Scenefiles/sur/Textures/v0022/tv_table_v0008_tvBodySG_Metalness.1001.png", "colorspace": "ACES - ACES2065-1", "type": "file", "udim": 1}, "tv_table_v0008_tvBodySG_BaseColor_1": {"plugs": ["baseColor"], "filepath": "D:/3D/working/projects/Generic/03_Workflow/Assets/tv_table/Scenefiles/sur/Textures/v0022/tv_table_v0008_tvBodySG_BaseColor.1001.png", "colorspace": "ACES - ACES2065-1", "type": "file", "udim": 1}}}}, "displacements": {"SAT_displacementShader1": {"type": "displacementShader", "texs": {"tv_table_v0008_tvBodySG_Height_1": {"plugs": ["displacementShader"], "filepath": "D:/3D/working/projects/Generic/03_Workflow/Assets/tv_table/Scenefiles/sur/Textures/v0022/tv_table_v0008_tvBodySG_Height.1001.png", "colorspace": "ACES - ACES2065-1", "type": "file", "udim": 1}}, "attrs": {}}}, "meshes": {"shape": ["|tv_table|tv|antenia|L_ball|L_ballShape", "|tv_table|tv|antenia|L_stand|L_standShape", "|tv_table|tv|antenia|R_ball|R_ballShape", "|tv_table|tv|antenia|R_stand|R_standShape", "|tv_table|tv|Sat_stand_leg5|Sat_stand_legShape5", "|tv_table|tv|Sat_stand_leg4|Sat_stand_legShape4", "|tv_table|tv|Sat_stand_leg3|Sat_stand_legShape3", "|tv_table|tv|Sat_stand_leg2|Sat_stand_legShape2", "|tv_table|tv|Sat_stand_leg1|Sat_stand_legShape1", "|tv_table|tv|antenia|Sat_stand|Sat_standShape", "|tv_table|tv|antenia|SAT_L|SAT_LShape", "|tv_table|tv|antenia|SAT_R|SAT_RShape", "|tv_table|tv|antenia|circle15|circle15Shape", "|tv_table|tv|antenia|circle16|circle16Shape"]}}, "tvScreenSG": {"materials": {"tvScreenMTL": {"type": "aiStandardSurface", "attrs": {"normalCamera": [[0.0, 0.0, 0.0]], "baseColor": [[0.0, 0.0, 0.0]], "specular": 0.4000000059604645, "specularColor": [[0.5290322303771973, 0.5290322303771973, 0.5290322303771973]], "specularRoughness": 0.0, "metalness": 1.0}, "texs": {}}}, "displacements": {}, "meshes": {"shape": ["|tv_table|tv|screen|screenShape"]}}, "tvBodySG": {"materials": {"tvBodyMTL": {"type": "aiStandardSurface", "attrs": {"normalCamera": [[0.0, 0.0, 0.0]], "baseColor": [[0.0, 0.0, 0.0]], "specularRoughness": 1.0, "metalness": 1.0}, "texs": {}}}, "displacements": {}, "meshes": {"shape": ["|tv_table|tv|W_slice24|W_sliceShape24", "|tv_table|tv|buttons|W_slice23|W_sliceShape23", "|tv_table|tv|buttons|W_slice22|W_sliceShape22", "|tv_table|tv|buttons|W_slice21|W_sliceShape21", "|tv_table|tv|buttons|W_slice20|W_sliceShape20", "|tv_table|tv|buttons|W_slice19|W_sliceShape19", "|tv_table|tv|buttons|W_slice18|W_sliceShape18", "|tv_table|tv|buttons|W_slice17|W_sliceShape17", "|tv_table|tv|buttons|W_slice16|W_sliceShape16", "|tv_table|tv|buttons|W_slice15|W_sliceShape15", "|tv_table|tv|buttons|W_slice14|W_sliceShape14", "|tv_table|tv|buttons|W_slice13|W_sliceShape13", "|tv_table|tv|buttons|W_slice12|W_sliceShape12", "|tv_table|tv|buttons|W_slice11|W_sliceShape11", "|tv_table|tv|buttons|W_slice10|W_sliceShape10", "|tv_table|tv|buttons|W_slice9|W_sliceShape9", "|tv_table|tv|buttons|W_slice8|W_sliceShape8", "|tv_table|tv|buttons|W_slice7|W_sliceShape7", "|tv_table|tv|buttons|W_slice6|W_sliceShape6", "|tv_table|tv|buttons|W_slice5|W_sliceShape5", "|tv_table|tv|buttons|W_slice4|W_sliceShape4", "|tv_table|tv|buttons|W_slice3|W_sliceShape3", "|tv_table|tv|buttons|W_slice2|W_sliceShape2", "|tv_table|tv|buttons|W_slice1|W_sliceShape1", "|tv_table|tv|buttons|polySurface197|polySurfaceShape210", "|tv_table|tv|polySurface198|polySurfaceShape211", "|tv_table|tv|buttons|polySurface107|polySurfaceShape109", "|tv_table|tv|buttons|plan|planShape", "|tv_table|tv|buttons|M_plan|M_planShape", "|tv_table|tv|buttons|slider7|sliderShape7", "|tv_table|tv|buttons|slider6|sliderShape6", "|tv_table|tv|buttons|slider5|sliderShape5", "|tv_table|tv|buttons|slider4|sliderShape4", "|tv_table|tv|buttons|slider3|sliderShape3", "|tv_table|tv|buttons|slider2|sliderShape2", "|tv_table|tv|buttons|Button10|ButtonShape10", "|tv_table|tv|buttons|Button9|ButtonShape9", "|tv_table|tv|buttons|Button8|ButtonShape8", "|tv_table|tv|buttons|Button7|ButtonShape7", "|tv_table|tv|buttons|Button6|ButtonShape6", "|tv_table|tv|buttons|Button5|ButtonShape5", "|tv_table|tv|buttons|Button4|ButtonShape4", "|tv_table|tv|buttons|Button3|ButtonShape3", "|tv_table|tv|buttons|Button2|ButtonShape2", "|tv_table|tv|buttons|Button1|ButtonShape1", "|tv_table|tv|rubber|rubberShape", "|tv_table|tv|buttons|Satalite|SataliteShape", "|tv_table|tv|leg2|legShape2", "|tv_table|tv|leg1|legShape1"]}}}}
    data["geo_type"] = "abc_ref"
    x = f'''
import sys
import os
sys.path.append(os.getenv("DJED_ROOT")+"/src")
sys.argv[0] = {data}
from dcc.clarisse.plugins import load_asset

import importlib
importlib.reload(load_asset)

load_asset.main()

    '''



    port.run(x)
