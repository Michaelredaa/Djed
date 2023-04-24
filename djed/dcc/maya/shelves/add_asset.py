# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, ]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.dcc.maya.shelves.ui.template import Button
from djed.utils.dialogs import message

import maya.cmds as cmds

# ---------------------------------
# Variables
djed_order = 1.00
djed_annotation = "To add a new asset and set working to selected asset"
djed_icon = "add.png"
djed_color = (0.9, 0.9, 0.9)
djed_backColor = (0.0, 0.0, 0.0, 0.0)
djed_imgLabel = ""


# ---------------------------------
# Start Here
class AddAsset(Button):
    title = "Add Asset"
    icon = "add.png"

    asset_name = ""

    def generate_ui(self):

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addItem(QSpacerItem(150, 20))
        self.rb_new = QRadioButton("New")
        self.rb_new.setChecked(True)
        self.rb_exist = QRadioButton("Existence")
        hbox.addWidget(self.rb_new)
        hbox.addWidget(self.rb_exist)
        vbox.addLayout(hbox)

        gbox = QGridLayout()
        gbox.addItem(QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum), 0, 0)

        # asset name
        hbox = QHBoxLayout()
        gbox.addWidget(QLabel("Asset Name: "), 1, 1, 1, 1, Qt.AlignRight)
        self.le_asset_name = QLineEdit()
        self.btn_selected_obj = QPushButton("<<<")
        hbox.addWidget(self.le_asset_name)
        hbox.addWidget(self.btn_selected_obj)
        gbox.addLayout(hbox, 1, 2, 1, 1, Qt.AlignRight)

        # tags
        gbox.addWidget(QLabel("Tags: "), 2, 1, 1, 1, Qt.AlignRight)
        self.tags = QLineEdit()
        gbox.addWidget(self.tags, 2, 2, 1, 1)
        gbox.addItem(QSpacerItem(80, 20, QSizePolicy.Minimum, QSizePolicy.Minimum), 2, 3)

        # description
        gbox.addWidget(QLabel("Description: "), 3, 1, 1, 1, Qt.AlignRight)
        self.description = QTextEdit()
        gbox.addWidget(self.description, 3, 2, 1, 1)
        gbox.addItem(QSpacerItem(80, 20, QSizePolicy.Minimum, QSizePolicy.Minimum), 2, 3)

        # thumbnail
        gbox.addWidget(QLabel("Thumbnail: "), 4, 1, 1, 1, Qt.AlignRight)
        self.lb_thumbnail = QLabel()
        preview = QPixmap(QPixmap(":/icons/empty_asset.png"))
        preview = preview.scaled(
            QSize(200, 200), Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.lb_thumbnail.setPixmap(preview)
        self.lb_thumbnail.setMargin(3)
        self.lb_thumbnail.installEventFilter(self)
        # self.lb_thumbnail.setStyleSheet("""background-color: rgba(0, 0, 0, 30)""")
        gbox.addWidget(self.lb_thumbnail, 4, 2, 1, 1, Qt.AlignLeft)
        gbox.addItem(QSpacerItem(80, 20, QSizePolicy.Minimum, QSizePolicy.Minimum), 2, 3)

        vbox.addLayout(gbox)

        self.vl_space.addLayout(vbox)
        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        self.on_selected_clicked()

    def connect_events(self):
        self.btn_selected_obj.clicked.connect(self.on_selected_clicked)

    def on_selected_clicked(self):
        selected = cmds.ls(sl=1)

        if not selected:
            message(self, "Warning", "You should select root group")
            return

        if len(selected) > 1:
            message(self, "Warning", "You should one group")
            return

        # check if the selected is a group
        if cmds.listRelatives(selected[0], s=1):
            message(self, "Warning", "You should select root group")
            return

        self.le_asset_name.setText(selected[0])

        self.asset_name = selected[0]

    def reset_ui(self):
        pass

    def apply(self):
        if not self.asset_name:
            ...

    def help(self):
        pass


def left_click():
    btn = AddAsset()
    btn.show()


def right_click():
    pass


def double_click():
    pass

