# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
from pathlib import Path

from PySide2.QtWidgets import *
from PySide2.QtGui import *

DJED_ROOT = Path(os.getenv('DJED_ROOT'))
sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from startup.system_tray import DjedTray

def run_tray():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    parent = QWidget()
    icon_path = f"{DJED_ROOT}/src/utils/resources/icons/djed.png"
    tray = DjedTray(QIcon(icon_path), parent)

    sys.exit(app.exec_())

def main():
    run_tray()




if __name__ == '__main__':
    print("Starting Djed")
    main()

