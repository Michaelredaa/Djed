# -*- coding: utf-8 -*-
"""
Documentation:
"""
import sys
import os
from datetime import datetime
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)


from PySide2.QtWidgets import QMessageBox
from PySide2.QtGui import QPixmap, QIcon

from djed.utils.resources.style_rc import *
from djed.version import version

def message(parent=None):
    year = datetime.now().year

    about = QMessageBox(parent)
    about.setWindowTitle("Djed Tools")
    about.setWindowIcon(QIcon(":/icons/about.png"))
    about.setInformativeText(f'''
    <blockquote skip="true">
        <h2><strong>Djed Tools</strong></h2>
    </blockquote>
    <p>Open-source assets pipeline that can manage the assets workflow.</p>
    <p><a href="https://github.com/Michaelredaa/Djed">https://github.com/Michaelredaa/Djed</a></p>
    <pstyle="margin-left: 40px;">Version: {version}</p>
    <pre>{year} Djed, All rights reserved</pre>
    <p><br></p>
        ''')
    pixmap = QPixmap(":/icons/djed.ico")
    pixmap.scaled(20, 20)

    about.setIconPixmap(pixmap)
    about.show()
    about.exec_()


if __name__ == '__main__':
    message()
    print(__name__)
