# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'djed')

sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.unreal.api.open_socket import listen

import unreal

unreal.log('Stating Djed receiving data...')

listen(host="127.0.0.1", port=55100)

unreal.log('listen...')

if __name__ == '__main__':
    print(__name__)
