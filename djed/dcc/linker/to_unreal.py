# -*- coding: utf-8 -*-
"""
Documentation:
"""
# ---------------------------------
# import libraries
import os
import sys
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))

sysPaths = [DJED_ROOT.as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.settings.settings import get_dcc_cfg
from djed.utils.open_ports import OpenSocket


def send_to_unreal(data, port_num=None):
    try:
        if not port_num:
            port_num = get_dcc_cfg("unreal", 'configuration', "command_port")

        unreal_socket = OpenSocket(host='127.0.0.1', port=port_num)

        cmd_text = "## Djed Tools ##\n\n"
        cmd_text += "print('## Djed Tools ##')\n"
        cmd_text += "print('[Djed] Start of receiving data')\n"
        cmd_text += "import sys, os, traceback\n"
        cmd_text += "sys.path.append(os.getenv('DJED_ROOT') + '/djed')\n"
        cmd_text += "try:\n"
        cmd_text += "\tfrom dcc.unreal.plugins.load_asset import LoadAsset\n"
        cmd_text += "\timport importlib;import dcc.unreal.plugins.load_asset;importlib.reload(dcc.unreal.plugins.load_asset)\n"
        cmd_text += "\tfrom dcc.linker.instance import create_instance\n"
        cmd_text += f"\tinstance = create_instance({data})\n"
        cmd_text += f"\tLoadAsset().process(instance)\n"
        cmd_text += f"except:\n"
        cmd_text += f"\tprint(traceback.format_exc())\n"
        cmd_text += "print('[Djed] End of receiving data')\n"

        unreal_socket.send(f'py {cmd_text}')

    except Exception as e:
        print(e)
        # message(None, "Error", str(e))


if __name__ == '__main__':
    data = {
        "family": "asset",
        "name": "wing",
        "renderer": "unreal",
        "geo_paths": {
            "obj": "C:/Users/michael/Documents/projects/dummy/scenes/Export/the_wing/v0001/the_wing.obj",
            "abc": "C:/Users/michael/Documents/projects/dummy/scenes/Export/the_wing/v0001/the_wing.abc"
        },
        "asset_data": {"wingSG": {"meshes": {
            "shape": ["|the_wing|Steel|bottom|bottomShape", "|the_wing|Rubber_dotted|Rubber_dottedShape",
                      "|the_wing|Steel|tail|tailShape", "|the_wing|cupper|polySurface1|polySurfaceShape2",
                      "|the_wing|Bronze_mat|Bronze_matShape",
                      "|the_wing|Red_bolt|pasted__polySurface50|pasted__polySurface50Shape",
                      "|the_wing|Steel|steel_top|steel_topShape", "|the_wing|bolts|boltsShape",
                      "|the_wing|cupper|polySurface3|polySurfaceShape4", "|the_wing|wood|Group16519|Group16519Shape",
                      "|the_wing|Steel|head|headShape", "|the_wing|cupper|polySurface2|polySurfaceShape3",
                      "|the_wing|back_gun|back_gunShape"]}, "materials": {"wingMTL": {"texs": {
            "wingSG_base_color": {"plugs": ["base_color"], "type": "file", "udim": 3,
                                  "filepath": "C:/Users/michael/Documents/projects/dummy/scenes/modeling/the_wing/sur/substance/textures/v0008/the_wing_wingSG_BaseColor.1001.png"},
            "wingSG_roughness": {"plugs": ["roughness"], "type": "file", "udim": 3,
                                 "filepath": "C:/Users/michael/Documents/projects/dummy/scenes/modeling/the_wing/sur/substance/textures/v0008/the_wing_wingSG_Roughness.1001.png"},
            "wingSG_metallic": {"plugs": ["metallic"], "type": "file", "udim": 3,
                                "filepath": "C:/Users/michael/Documents/projects/dummy/scenes/modeling/the_wing/sur/substance/textures/v0008/the_wing_wingSG_Metalness.1001.png"},
            "wingSG_normal": {"plugs": ["normal"], "type": "file", "udim": 3,
                              "filepath": "C:/Users/michael/Documents/projects/dummy/scenes/modeling/the_wing/sur/substance/textures/v0008/the_wing_wingSG_Normal.1001.png"}},
                                                                                      "attrs": {},
                                                                                      "type": "standard_surface"}},
                                  "displacements": {"wingSG_displacement": {"texs": {
                                      "wingSG_height": {"plugs": ["height"], "type": "file", "udim": 3,
                                                        "filepath": "C:/Users/michael/Documents/projects/dummy/scenes/modeling/the_wing/sur/substance/textures/v0008/the_wing_wingSG_Height.1001.png"}},
                                                                            "attrs": {}, "type": "displacement"}}}}
    }

    send_to_unreal(data)

    print(__name__)
