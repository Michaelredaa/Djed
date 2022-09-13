# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_tag.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from lib.assets_browser.promoted_widgets import LineEdit

class Ui_addTagWidget(object):
    def setupUi(self, addTagWidget):
        if not addTagWidget.objectName():
            addTagWidget.setObjectName(u"addTagWidget")
        addTagWidget.resize(346, 200)
        self.gridLayout_3 = QGridLayout(addTagWidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.frame_3 = QFrame(addTagWidget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_7)

        self.pb_add_tag = QPushButton(self.frame_3)
        self.pb_add_tag.setObjectName(u"pb_add_tag")

        self.horizontalLayout_3.addWidget(self.pb_add_tag)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.pb_close = QPushButton(self.frame_3)
        self.pb_close.setObjectName(u"pb_close")

        self.horizontalLayout_3.addWidget(self.pb_close)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 4, 0, 1, 1)

        self.frame = QFrame(self.frame_3)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 0, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_5, 0, 2, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.cb_project = QCheckBox(self.frame)
        self.cb_project.setObjectName(u"cb_project")
        self.cb_project.setMinimumSize(QSize(150, 0))
        self.cb_project.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout_2.addWidget(self.cb_project)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.le_tags = LineEdit(self.frame)
        self.le_tags.setObjectName(u"le_tags")
        self.le_tags.setMinimumSize(QSize(150, 0))
        self.le_tags.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout.addWidget(self.le_tags)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)

        self.l_tags = QGridLayout()
        self.l_tags.setSpacing(0)
        self.l_tags.setObjectName(u"l_tags")

        self.horizontalLayout_4.addLayout(self.l_tags)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_9)


        self.gridLayout_2.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)

        self.line = QFrame(self.frame_3)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 3, 0, 1, 1)


        self.gridLayout_3.addWidget(self.frame_3, 0, 0, 2, 2)


        self.retranslateUi(addTagWidget)

        QMetaObject.connectSlotsByName(addTagWidget)
    # setupUi

    def retranslateUi(self, addTagWidget):
        addTagWidget.setWindowTitle(QCoreApplication.translate("addTagWidget", u"Form", None))
        self.pb_add_tag.setText(QCoreApplication.translate("addTagWidget", u"Add", None))
        self.pb_close.setText(QCoreApplication.translate("addTagWidget", u"Close", None))
        self.cb_project.setText(QCoreApplication.translate("addTagWidget", u"As project tag", None))
        self.le_tags.setPlaceholderText(QCoreApplication.translate("addTagWidget", u"Add tag and press enter", None))
    # retranslateUi

