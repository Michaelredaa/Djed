# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
from pathlib import Path

from PySide2.QtWidgets import *
from PySide2.QtGui import *

from utils.startup.system_tray import DjedTray

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

    app = QApplication(sys.argv)
    parent = QWidget()
    icon = QIcon(os.path.join(os.getenv('DJED_ROOT'), 'src', 'utils', 'resources', 'icons', 'djed.png'))
    tray = DjedTray(icon, parent)

    sys.exit(app.exec_())
