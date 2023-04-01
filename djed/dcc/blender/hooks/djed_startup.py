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

import importlib
import djed.utils.open_ports as op

importlib.reload(op)

bl_server = op.SimpleServer(host='localhost', port=55200)


def register():
    bl_server.run()


def deregister():
    if bl_server.Instance:
        bl_server.Instance[0].thread_complete()
        bl_server.Instance = []


register()
