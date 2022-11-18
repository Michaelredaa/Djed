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
from utils.resources.style_rc import *


def run_tray():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    parent = QWidget()
    tray = DjedTray(QIcon(":/icons/djed.png"), parent)

    sys.exit(app.exec_())


def main():
    run_tray()


if __name__ == '__main__':
    print("Starting Djed")
    main()
