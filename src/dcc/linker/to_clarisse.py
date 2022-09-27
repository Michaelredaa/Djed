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

    data ={'family': 'asset', 'name': 'chair', 'file_color_space': ['ACEScg', 'ACES2065-1', 'scene-linear Rec.709-sRGB', 'scene-linear DCI-P3 D65', 'scene-linear Rec.2020'], 'renderer': 'arnold', 'host': 'maya', 'geo_paths': {'obj': 'C:/Users/michael/Documents/projects/dummy/scenes/Export/chair/chair_v0019.obj', 'abc': 'C:/Users/michael/Documents/projects/dummy/scenes/Export/chair/chair_v0019.abc'}, 'asset_data': {'chairSG': {'materials': {'chairMTL': {'type': 'aiStandardSurface', 'attrs': {'baseColor': [(0.0, 0.0, 0.0)], 'specularRoughness': 1.0}, 'texs': {'ukjneb3bw_2K_Albedo_1': {'plugs': ['baseColor'], 'filepath': 'C:/Users/michael/Documents/Quixel_assets/Downloaded/3d/interior_furniture_ukjneb3bw/ukjneb3bw_2K_Albedo.jpg', 'colorspace': 'sRGB', 'type': 'file'}, 'ukjneb3bw_2K_Normal_LOD1_1': {'plugs': ['normalCamera'], 'filepath': 'C:/Users/michael/Documents/Quixel_assets/Downloaded/3d/interior_furniture_ukjneb3bw/ukjneb3bw_2K_Normal_LOD1.jpg', 'colorspace': 'sRGB', 'type': 'file'}, 'ukjneb3bw_2K_Roughness_1': {'plugs': ['specularRoughness'], 'filepath': 'C:/Users/michael/Documents/Quixel_assets/Downloaded/3d/interior_furniture_ukjneb3bw/ukjneb3bw_2K_Roughness.jpg', 'colorspace': 'sRGB', 'type': 'file'}}}}, 'displacements': {}, 'meshes': {'shape': ['|chair|chair1|chair1Shape']}}}}
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
