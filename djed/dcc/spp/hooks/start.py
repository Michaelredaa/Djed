# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
import shutil
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))
sysPaths = [DJED_ROOT.as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.utils.sys_process import create_shortcut
from djed.settings.settings import get_dcc_cfg


def create_spp_shortcut():
    spp_exe = get_dcc_cfg("substance_painter", "configuration", "executable")
    create_shortcut(
        f'{os.getenv("PROGRAMDATA")}/Microsoft/Windows/Start Menu/Programs/Djed Adobe Substance 3D Painter.lnk',
        spp_exe,
        '--enable-remote-scripting',
        spp_exe,
    )


def add_spp_startup():
    source_file = DJED_ROOT.joinpath('djed/dcc/spp/hooks/djed_startup.py')
    dist_file = Path.home().joinpath("Documents/Adobe/Adobe Substance 3D Painter/python/startup/djed_startup.py")
    if dist_file.is_file():
        try:
            dist_file.unlink(missing_ok=True)
        except:
            pass

    if not dist_file.parent.is_dir():
        dist_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy(source_file, dist_file)
        return "Done"
    except:
        return 'Unable to add integration to substance painter'


if __name__ == '__main__':
    print(__name__)
