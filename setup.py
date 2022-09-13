# -*- coding: utf-8 -*-
"""
Documentation:
"""

from pathlib import Path
from PySide2 import *


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
    set_environment()
    print("Starting Djed")
