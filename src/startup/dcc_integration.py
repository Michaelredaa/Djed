# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))
sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.maya.hooks.start import add_maya_module
from dcc.spp.hooks.start import add_spp_startup
from dcc.clarisse.hooks.start import add_clarisse_shelf


def add_djed_integration():
    msg = []
    msg.append(f'<p><span style="font-size: 20px;">Maya integration: </span> {add_maya_module()}</p>')
    msg.append(f'<p><span style="font-size: 20px;">Substance painter integration: </span> {add_spp_startup()}</p>')
    msg.append(f'<p><span style="font-size: 20px;">Clarisse integration: </span> {add_clarisse_shelf()}</p>')

    return '\n'.join(msg)


if __name__ == '__main__':
    print(__name__)
