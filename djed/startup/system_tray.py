# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
import time

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, DJED_ROOT + '/djed']
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from lib.assets_browser.window import AssetViewWindow
from settings.settings_window import SettingsWindow
from startup.dcc_integration import add_djed_integration
from utils.resources.stylesheet import get_stylesheet
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

        self.settings_win = None
        self.browser_win = None

        self.on_splash_start()
        # start_timer = QTimer()
        # start_timer.setInterval(100)
        # start_timer.start()
        # start_timer.timeout.connect(self.on_splash_start)

        self.show()

        # self.showMessage('Djed', 'Starting')

    def create_menus(self):
        menu = QMenu(self._parent)

        djed_action = menu.addAction("Djed Tools")

        menu.addSeparator()

        asset_browser_action = menu.addAction(QIcon(":/icons/assetIcon.png"), "Assets Browser")
        asset_browser_action.triggered.connect(self.on_open_asset_browser)

        settings_action = menu.addAction(QIcon(":/icons/settings.png"), "Settings")
        settings_action.triggered.connect(self.on_open_settings)

        menu.addSeparator()
        close_action = menu.addAction(QIcon(":/icons/close.png"), "Close")
        close_action.triggered.connect(lambda: sys.exit())

        menu.addSeparator()

        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_activated)

        menu.setStyleSheet(get_stylesheet())

    def init_environment(self):
        self.add_integration()

    def on_open_asset_browser(self):
        if self.browser_win is None:
            self.browser_win = AssetViewWindow()
        self.browser_win.show()

    def on_open_settings(self):
        if self.settings_win is None:
            self.settings_win = SettingsWindow()
        self.settings_win.show()

    def on_splash_start(self):
        pixmap = QPixmap(":/icons/djed.ico")
        splash = QSplashScreen(pixmap)
        splash.setMask(pixmap.mask())
        splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        splash.show()

        QTimer.singleShot(2000, splash.close)
        time.sleep(2)

    def add_integration(self):
        msg_txt = add_djed_integration()

    def on_tray_activated(self, action):
        if action == self.DoubleClick:
            self.on_open_asset_browser()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parent = QWidget()
    icon_path = f"{DJED_ROOT}/djed/utils/resources/icons/djed.png"
    icon = QIcon(icon_path)
    tray = DjedTray(icon, parent)

    sys.exit(app.exec_())
