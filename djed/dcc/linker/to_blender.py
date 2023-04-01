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


def is_blender_connected(port_num=None):
    if not port_num:
        port_num = get_dcc_cfg("blender", 'configuration', "command_port")
    socket = OpenSocket(host='localhost', port=port_num)
    return socket


def send_to_blender(data, port_num=None):
    try:
        blender_port = is_blender_connected(port_num=port_num)


        cmd_text = "## Djed Tools ##\n\n"
        cmd_text += "print('## Djed Tools ##')\n"
        cmd_text += "print('[Djed] Start of receiving data')\n"
        cmd_text += "import sys, os, traceback\n"
        cmd_text += "sys.path.append(os.getenv('DJED_ROOT'))\n"

        cmd_text += "try:\n"
        cmd_text += "\timport importlib;import djed.dcc.blender.plugins.load_asset\n"
        cmd_text += "\timportlib.reload(djed.dcc.blender.plugins.load_asset)\n"

        cmd_text += "\tfrom djed.dcc.linker.instance import create_instance\n"
        cmd_text += "\tfrom djed.dcc.blender.plugins.load_asset import LoadAsset\n"

        cmd_text += f"\tinstance = create_instance({data})\n"
        cmd_text += f"\tLoadAsset().process(instance)\n"
        cmd_text += f"except:\n"
        cmd_text += f"\tprint(traceback.format_exc())\n"
        cmd_text += "print('[Djed] End of receiving data')\n"

        blender_port.send(f'{cmd_text}')

    except Exception as e:
        print(e)
        # message(None, "Error", str(e))
