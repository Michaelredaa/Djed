# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# import libraries
import sys
import os

DJED_ROOT = os.getenv('DJED_ROOT')

sysPaths = [DJED_ROOT]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import djed.utils.open_ports as op
from djed.settings.settings import get_dcc_cfg


port_num = get_dcc_cfg("blender", 'configuration', "command_port")
bl_server = op.SimpleServer(host='localhost', port=port_num)


def register():
    bl_server.run()


def deregister():
    if bl_server.Instance:
        bl_server.Instance[0].thread_complete()
        bl_server.Instance = []


register()
