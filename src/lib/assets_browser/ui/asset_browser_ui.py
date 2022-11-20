# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'asset_browser_ui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from lib.assets_browser.ui.promoted_widgets import ListView


class Ui_AssetBrowserWindow(object):
    def setupUi(self, AssetBrowserWindow):
        if not AssetBrowserWindow.objectName():
            AssetBrowserWindow.setObjectName(u"AssetBrowserWindow")
        AssetBrowserWindow.resize(1204, 644)
        self.centralwidget = QWidget(AssetBrowserWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.splitter_3 = QSplitter(self.centralwidget)
        self.splitter_3.setObjectName(u"splitter_3")
        self.splitter_3.setLineWidth(3)
        self.splitter_3.setOrientation(Qt.Horizontal)
        self.splitter_3.setHandleWidth(7)
        self.splitter_2 = QSplitter(self.splitter_3)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setLineWidth(3)
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.splitter_2.setHandleWidth(7)
        self.layoutWidget_2 = QWidget(self.splitter_2)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_6 = QSpacerItem(50, 2, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_6)

        self.pushButton_sortItems = QPushButton(self.layoutWidget_2)
        self.pushButton_sortItems.setObjectName(u"pushButton_sortItems")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_sortItems.sizePolicy().hasHeightForWidth())
        self.pushButton_sortItems.setSizePolicy(sizePolicy)
        self.pushButton_sortItems.setMinimumSize(QSize(0, 20))
        self.pushButton_sortItems.setMaximumSize(QSize(40, 25))
        self.pushButton_sortItems.setStyleSheet(u"background-color:none;\n"
                                                "border:none;\n"
                                                "padding: 2px 2px 2px 2px;")
        icon = QIcon()
        icon.addFile(u":/ui/icon/images/sort.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_sortItems.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.pushButton_sortItems)

        self.pushButton_refreshView = QPushButton(self.layoutWidget_2)
        self.pushButton_refreshView.setObjectName(u"pushButton_refreshView")
        sizePolicy.setHeightForWidth(self.pushButton_refreshView.sizePolicy().hasHeightForWidth())
        self.pushButton_refreshView.setSizePolicy(sizePolicy)
        self.pushButton_refreshView.setMinimumSize(QSize(0, 20))
        self.pushButton_refreshView.setMaximumSize(QSize(40, 25))
        self.pushButton_refreshView.setStyleSheet(u"background-color:none;\n"
                                                  "border:none;\n"
                                                  "padding: 2px 2px 2px 2px;")
        icon1 = QIcon()
        icon1.addFile(u":/icons/reload.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_refreshView.setIcon(icon1)
        self.pushButton_refreshView.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.pushButton_refreshView)

        self.pushButton_filterItems = QPushButton(self.layoutWidget_2)
        self.pushButton_filterItems.setObjectName(u"pushButton_filterItems")
        sizePolicy.setHeightForWidth(self.pushButton_filterItems.sizePolicy().hasHeightForWidth())
        self.pushButton_filterItems.setSizePolicy(sizePolicy)
        self.pushButton_filterItems.setMinimumSize(QSize(0, 25))
        self.pushButton_filterItems.setMaximumSize(QSize(40, 25))
        self.pushButton_filterItems.setStyleSheet(u"background-color:none;\n"
                                                  "border:none;\n"
                                                  "padding: 2px 2px 2px 2px;")
        icon2 = QIcon()
        icon2.addFile(u":/icons/filter.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_filterItems.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.pushButton_filterItems)

        self.le_search = QLineEdit(self.layoutWidget_2)
        self.le_search.setObjectName(u"le_search")
        self.le_search.setMinimumSize(QSize(150, 0))
        self.le_search.setMaximumSize(QSize(170, 16777215))
        self.le_search.setStyleSheet(u"")

        self.horizontalLayout_2.addWidget(self.le_search)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lw_assets = ListView(self.layoutWidget_2)
        self.lw_assets.setObjectName(u"lw_assets")
        self.lw_assets.setMinimumSize(QSize(900, 0))

        self.verticalLayout_2.addWidget(self.lw_assets)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.asset_num = QLabel(self.layoutWidget_2)
        self.asset_num.setObjectName(u"asset_num")

        self.horizontalLayout.addWidget(self.asset_num)

        self.horizontalSpacer = QSpacerItem(120, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalSlider = QSlider(self.layoutWidget_2)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setMaximumSize(QSize(150, 16777215))
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout.addWidget(self.horizontalSlider)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)

        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.splitter_2.addWidget(self.layoutWidget_2)
        self.splitter_3.addWidget(self.splitter_2)
        self.splitter = QSplitter(self.splitter_3)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setLineWidth(3)
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setOpaqueResize(True)
        self.splitter.setHandleWidth(7)
        self.layoutWidget_3 = QWidget(self.splitter)
        self.layoutWidget_3.setObjectName(u"layoutWidget_3")
        self.verticalLayout_5 = QVBoxLayout(self.layoutWidget_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.tabWidget_2 = QTabWidget(self.layoutWidget_3)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy1)
        self.tabWidget_2.setMinimumSize(QSize(265, 265))
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_6 = QGridLayout(self.tab_2)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.frame_3d = QFrame(self.tab_2)
        self.frame_3d.setObjectName(u"frame_3d")
        self.frame_3d.setFrameShape(QFrame.StyledPanel)
        self.frame_3d.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_3d)
        self.gridLayout_3.setObjectName(u"gridLayout_3")

        self.verticalLayout_7.addWidget(self.frame_3d)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_7.addItem(self.verticalSpacer)


        self.gridLayout_6.addLayout(self.verticalLayout_7, 0, 0, 1, 1)

        self.tabWidget_2.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tab_3.setMaximumSize(QSize(1000, 1000))
        self.gridLayout_5 = QGridLayout(self.tab_3)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.label_preview0 = QLabel(self.tab_3)
        self.label_preview0.setObjectName(u"label_preview0")
        sizePolicy1.setHeightForWidth(self.label_preview0.sizePolicy().hasHeightForWidth())
        self.label_preview0.setSizePolicy(sizePolicy1)
        self.label_preview0.setMinimumSize(QSize(128, 128))
        self.label_preview0.setMaximumSize(QSize(512, 512))

        self.horizontalLayout_4.addWidget(self.label_preview0)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)


        self.verticalLayout_11.addLayout(self.horizontalLayout_4)


        self.verticalLayout_10.addLayout(self.verticalLayout_11)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")

        self.verticalLayout_10.addLayout(self.horizontalLayout_6)


        self.verticalLayout_8.addLayout(self.verticalLayout_10)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_8.addItem(self.verticalSpacer_2)


        self.gridLayout_5.addLayout(self.verticalLayout_8, 0, 0, 1, 1)

        self.tabWidget_2.addTab(self.tab_3, "")

        self.verticalLayout_5.addWidget(self.tabWidget_2)

        self.splitter.addWidget(self.layoutWidget_3)
        self.gridLayoutWidget = QWidget(self.splitter)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.table_data = QTreeWidget(self.gridLayoutWidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.table_data.setHeaderItem(__qtreewidgetitem)
        self.table_data.setObjectName(u"table_data")

        self.gridLayout_2.addWidget(self.table_data, 0, 0, 1, 1)

        self.splitter.addWidget(self.gridLayoutWidget)
        self.splitter_3.addWidget(self.splitter)

        self.gridLayout.addWidget(self.splitter_3, 0, 0, 1, 1)

        AssetBrowserWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(AssetBrowserWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1204, 21))
        AssetBrowserWindow.setMenuBar(self.menubar)

        self.retranslateUi(AssetBrowserWindow)

        self.tabWidget_2.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(AssetBrowserWindow)
    # setupUi

    def retranslateUi(self, AssetBrowserWindow):
        AssetBrowserWindow.setWindowTitle(QCoreApplication.translate("AssetBrowserWindow", u"MainWindow", None))
        # if QT_CONFIG(tooltip)
        self.pushButton_sortItems.setToolTip(QCoreApplication.translate("AssetBrowserWindow", u"Sort Items", None))
        # endif // QT_CONFIG(tooltip)
        self.pushButton_sortItems.setText("")
        # if QT_CONFIG(tooltip)
        self.pushButton_refreshView.setToolTip(QCoreApplication.translate("AssetBrowserWindow", u"Sort Items", None))
        # endif // QT_CONFIG(tooltip)
        self.pushButton_refreshView.setText("")
        # if QT_CONFIG(tooltip)
        self.pushButton_filterItems.setToolTip(QCoreApplication.translate("AssetBrowserWindow", u"Filter Items", None))
        # endif // QT_CONFIG(tooltip)
        self.pushButton_filterItems.setText("")
        # if QT_CONFIG(tooltip)
        self.le_search.setToolTip(QCoreApplication.translate("AssetBrowserWindow", u"Search Items", None))
        # endif // QT_CONFIG(tooltip)
        self.le_search.setPlaceholderText(QCoreApplication.translate("AssetBrowserWindow", u"Search", None))
        self.asset_num.setText(QCoreApplication.translate("AssetBrowserWindow", u"0 Asset", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_2), QCoreApplication.translate("AssetBrowserWindow", u"3D", None))
        self.label_preview0.setText("")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), QCoreApplication.translate("AssetBrowserWindow", u"Image", None))
    # retranslateUi

