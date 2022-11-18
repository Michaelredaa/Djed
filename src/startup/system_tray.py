# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys

from PySide2.QtWidgets import *
from PySide2.QtGui import *

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, DJED_ROOT+'/src']
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)


from lib.assets_browser.window import AssetViewWindow
from settings.settings_window import SettingsWindow
from utils.resources.style_rc import *


class DjedTray(QSystemTrayIcon):
    """
    Creates a system tray
    """

    def __init__(self, icon, parent=None):
        super(DjedTray, self).__init__(icon, parent)
        self._parent = parent

        self.setToolTip('Djed tools')

        self.create_menus()
        self.init_environment()

        self.show()
        self.showMessage('Djed', 'Starting')


    def create_menus(self):
        menu = QMenu(self._parent)

        asset_browser_action = menu.addAction(QIcon(":/icons/assetIcon.png"), "Asset Browser")
        asset_browser_action.triggered.connect(self.on_open_asset_browser)

        settings_action = menu.addAction(QIcon(":/icons/settings.png"), "Settings")
        settings_action.triggered.connect(self.on_open_settings)

        menu.addSeparator()
        close_action = menu.addAction(QIcon(":/icons/close.png"), "Close")
        close_action.triggered.connect(lambda: sys.exit())

        menu.addSeparator()

        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_activated)

        menu.setStyleSheet(open(f"{DJED_ROOT}/src/utils/resources/stylesheet.qss").read())

    def init_environment(self):
        ...

    def on_open_asset_browser(self):
        win = AssetViewWindow()
        win.show()

    def on_open_settings(self):
        win = SettingsWindow()
        win.show()

    def on_tray_activated(self, action):
        if action == self.DoubleClick:
            print("Right")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parent = QWidget()
    icon_path = f"{DJED_ROOT}/src/utils/resources/icons/djed.png"
    icon = QIcon(icon_path)
    tray = DjedTray(icon, parent)

    sys.exit(app.exec_())
