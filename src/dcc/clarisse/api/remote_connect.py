# -*- coding: utf-8 -*-
"""
Documentation: 
"""


# ---------------------------------
# Import Libraries
import os
import sys
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)


from utils.file_manager import FileManager
from settings.settings import get_dcc_cfg
from utils import clarisse_net as ix
# ---------------------------------
# Variables


fm = FileManager()
# ---------------------------------
# Start Here
def set_port_num(port_num=None):
    if port_num is None:
        port_num = get_dcc_cfg("clarisse", 'configuration', "command_port")
    return port_num


def connect(ip='localhost', port_num=None):
    try:
        port_num = set_port_num(port_num)
        port = ix.ClarisseNet(ip, port_num)
        return port
    except Exception as e:
        print(e)
        pass
    return


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
