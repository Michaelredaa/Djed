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


def set_port_num(port_num=None):
    if port_num is None:
        port_num = fm.get_user_json("clarisse", "command_port")
    return port_num


def connect(ip='localhost'):
    try:
        port_num = set_port_num()
        port = ix.ClarisseNet(ip, port_num)
        return port
    except:
        pass
    return

    @error(name=__name__)
    def spp_to_clarisse(self, **kwargs):
        port = self.connect()
        if not port:
            return "Can not connect with clarisse port"
        cmd = "import sys\n"
        cmd += f"with open(r'{ClarissePort_path}', 'r') as f:\n"
        cmd += f"\tscript = f.read()\n"
        cmd += f"\tsys.argv = [r'{ClarissePort_path}', {kwargs}]\n"
        cmd += f"\texec(script)\n"

        port.run(cmd)
        return "Asset send successfully."

    @error(name=__name__)
    def maya_to_clarisse(self, mayaData, cfg=None):
        port = self.connect()
        if not port:
            return

        cmd = "import sys\n"
        cmd += f"with open(r'{ClarissePort_path}', 'r') as f:\n"
        cmd += f"\tscript = f.read()\n"
        cmd += f"\tsys.argv = [r'{ClarissePort_path}', {mayaData}, {cfg}]\n"
        cmd += f"\texec(script)\n"

        port.run(cmd)


if __name__ == '__main__':
    print(__name__)
