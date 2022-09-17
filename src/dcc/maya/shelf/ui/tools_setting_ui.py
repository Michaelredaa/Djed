# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tools_setting.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ToolSettings(object):
    def setupUi(self, ToolSettings):
        if not ToolSettings.objectName():
            ToolSettings.setObjectName(u"ToolSettings")
        ToolSettings.resize(607, 449)
        self.actionReset_Settings = QAction(ToolSettings)
        self.actionReset_Settings.setObjectName(u"actionReset_Settings")
        self.actionHelp_on_this_tool = QAction(ToolSettings)
        self.actionHelp_on_this_tool.setObjectName(u"actionHelp_on_this_tool")
        self.actionSave_Settings = QAction(ToolSettings)
        self.actionSave_Settings.setObjectName(u"actionSave_Settings")
        self.actionf = QAction(ToolSettings)
        self.actionf.setObjectName(u"actionf")
        self.centralwidget = QWidget(ToolSettings)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(0)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.vl_space = QVBoxLayout()
        self.vl_space.setObjectName(u"vl_space")
        self.vl_space.setSizeConstraint(QLayout.SetMaximumSize)
        self.vl_space.setContentsMargins(6, 6, 6, 6)

        self.gridLayout_3.addLayout(self.vl_space, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pb_apply = QPushButton(self.centralwidget)
        self.pb_apply.setObjectName(u"pb_apply")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(self.pb_apply.sizePolicy().hasHeightForWidth())
        self.pb_apply.setSizePolicy(sizePolicy)
        self.pb_apply.setMaximumSize(QSize(100, 25))

        self.horizontalLayout.addWidget(self.pb_apply)

        self.pb_save = QPushButton(self.centralwidget)
        self.pb_save.setObjectName(u"pb_save")
        sizePolicy.setHeightForWidth(self.pb_save.sizePolicy().hasHeightForWidth())
        self.pb_save.setSizePolicy(sizePolicy)
        self.pb_save.setMaximumSize(QSize(100, 25))

        self.horizontalLayout.addWidget(self.pb_save)

        self.pb_cancel = QPushButton(self.centralwidget)
        self.pb_cancel.setObjectName(u"pb_cancle")
        sizePolicy.setHeightForWidth(self.pb_cancel.sizePolicy().hasHeightForWidth())
        self.pb_cancel.setSizePolicy(sizePolicy)
        self.pb_cancel.setMaximumSize(QSize(100, 25))

        self.horizontalLayout.addWidget(self.pb_cancel)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        ToolSettings.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ToolSettings)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 607, 22))
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuRecent = QMenu(self.menuEdit)
        self.menuRecent.setObjectName(u"menuRecent")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        ToolSettings.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuEdit.addAction(self.actionSave_Settings)
        self.menuEdit.addAction(self.actionReset_Settings)
        self.menuEdit.addAction(self.menuRecent.menuAction())
        self.menuHelp.addAction(self.actionHelp_on_this_tool)

        self.retranslateUi(ToolSettings)

        QMetaObject.connectSlotsByName(ToolSettings)
    # setupUi

    def retranslateUi(self, ToolSettings):
        ToolSettings.setWindowTitle(QCoreApplication.translate("ToolSettings", u"Settings", None))
        self.actionReset_Settings.setText(QCoreApplication.translate("ToolSettings", u"Reset Settings", None))
        self.actionHelp_on_this_tool.setText(QCoreApplication.translate("ToolSettings", u"Help on this tool", None))
        self.actionSave_Settings.setText(QCoreApplication.translate("ToolSettings", u"Save Settings", None))
        self.actionf.setText(QCoreApplication.translate("ToolSettings", u"f", None))
        self.pb_apply.setText(QCoreApplication.translate("ToolSettings", u"Apply", None))
        self.pb_save.setText(QCoreApplication.translate("ToolSettings", u"Save and Close", None))
        self.pb_cancel.setText(QCoreApplication.translate("ToolSettings", u"Cancel", None))
        self.menuEdit.setTitle(QCoreApplication.translate("ToolSettings", u"Edit", None))
        self.menuRecent.setTitle(QCoreApplication.translate("ToolSettings", u"Recent", None))
        self.menuHelp.setTitle(QCoreApplication.translate("ToolSettings", u"Help", None))
    # retranslateUi

