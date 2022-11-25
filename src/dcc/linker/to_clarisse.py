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

sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from settings.settings import get_dcc_cfg
from utils.dialogs import message
from utils.file_manager import FileManager
from dcc.clarisse.api.remote_connect import connect

# ---------------------------------

# if not ix.application.is_command_port_active():
#     ix.application.enable_command_port()

fm = FileManager()


def is_clarisse_connected(port_num=None):
    if not port_num:
        port_num = get_dcc_cfg("clarisse", 'configuration', "command_port")
    socket = connect(ip='localhost', port_num=int(port_num))
    return socket


def send_to_clarisse(data, port_num=None):
    try:
        if not port_num:
            port_num = get_dcc_cfg("clarisse", 'configuration', "command_port")
        socket = connect(ip='localhost', port_num=int(port_num))

        cmd_text = "## Djed Tools ##\n\n"
        cmd_text += "print('## Djed Tools ##')\n"
        cmd_text += "print('[Djed] Start of receiving data')\n"
        cmd_text += "import sys, os, traceback\n"
        cmd_text += "sys.path.append(os.getenv('DJED_ROOT') + '/src')\n"
        cmd_text += "try:\n"
        cmd_text += "\tfrom dcc.clarisse.plugins.load_asset import LoadAsset\n"
        cmd_text += "\timport importlib;import dcc.clarisse.plugins.load_asset;importlib.reload(dcc.clarisse.plugins.load_asset)\n"
        cmd_text += "\tfrom dcc.linker.instance import create_instance\n"
        cmd_text += f"\tinstance = create_instance({data})\n"
        cmd_text += f"\tLoadAsset().process(instance)\n"
        cmd_text += f"except:\n"
        cmd_text += f"\tprint(traceback.format_exc())\n"
        cmd_text += "print('[Djed] End of receiving data')\n"

        socket.run(cmd_text)

    except Exception as e:
        message(None, "Error", str(e))


if __name__ == '__main__':
    print(is_clarisse_connected())
