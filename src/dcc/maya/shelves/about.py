# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# import libraries
import sys
import os
from pathlib import Path
import maya.cmds as cmds

from PySide2.QtWidgets import QMessageBox
from PySide2.QtGui import QPixmap, QIcon

# ---------------------------------
# MetaData
_annotation = "About"
_icon = "about.png"
_color = (0.9, 0.9, 0.9)
_backColor = (0.0, 0.0, 0.0, 0.0)
_imgLabel = ""

# ---------------------------------
DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from src.version import version
from dcc.maya.api.cmds import maya_main_window
from utils.resources.style_rc import *

# Main function
def main():
    about = QMessageBox(maya_main_window())
    about.setWindowTitle("Djed Tools")
    about.setWindowIcon(QIcon(":/icons/about.png"))
    about.setInformativeText(f'''
<blockquote skip="true">
    <h2><strong>Djed Tools</strong></h2>
</blockquote>
<p>Open-source assets pipeline that can manage the assets workflow.</p>
<p><a href="https://github.com/Michaelredaa/Djed">https://github.com/Michaelredaa/Djed</a></p>
<pstyle="margin-left: 40px;">Version: {version}</p>
<pre>2022 Djed, All rights reserved</pre>
<p><br></p>
    ''')
    pixmap = QPixmap(":/icons/djed.ico")
    pixmap.scaled(20, 20)

    about.setIconPixmap(pixmap)
    about.show()
    about.exec_()
    # cmds.confirmDialog(title='Djed Tools', message=version)


if __name__ == '__main__':
    main()
