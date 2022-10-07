# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
import traceback
from pathlib import Path

from PySide2.QtWidgets import *
from PySide2.QtGui import *

from utils.startup.system_tray import DjedTray

DJED_ROOT = Path(os.getenv('DJED_ROOT'))


def add_maya_module(maya_module_path=None):
    if maya_module_path is None:
        maya_module_path = Path.home().joinpath("Documents", "maya", "modules")
    else:
        maya_module_path = Path(str(maya_module_path))

    maya_module_path.mkdir(parents=True, exist_ok=True)
    mod_file = maya_module_path.joinpath("djed.mod")
    root_path = DJED_ROOT.joinpath('src/maya/hooks').as_posix()
    cmd = f'+ Djed 1.0 {root_path}\nscripts: {root_path}'

    #mod_file.unlink(missing_ok=True)

    with mod_file.open('w') as f:
        f.write(cmd)

def add_clarisse_shelf(env_path=None):
    if not env_path:
        env_path = os.path.join(os.environ["APPDATA"], "Isotropix", "Clarisse", "5.0", "clarisse.env")

    shelf_path = "$DJED_ROOT/src/dcc/clarisse/hooks/djed_shelf.cfg"
    text = []
    with open(env_path, "r") as fh:
        for line in fh:
            if "IX_SHELF_CONFIG_FILE" in line:
                if shelf_path in line:
                    return
                else:
                    text.append(line.strip()+";"+shelf_path+"\n")
            else:
                text.append(line)
    with open(env_path, "w") as fh2:
        fh2.writelines(text)

def set_environment():
    from ctypes import windll

    current_file = Path(__file__)

    bat_file_path = current_file.parent.joinpath('start.bat')
    result = windll.shell32.ShellExecuteW(
        None,  # handle to parent window
        'runas',  # verb
        'cmd.exe',  # file on which verb acts
        ' '.join(['/c', str(bat_file_path)]),  # parameters
        None,  # working directory (default is cwd)
        0,  # show window normally
    )
    success = result > 32






if __name__ == '__main__':
    print("Starting Djed")
    add_maya_module()

