#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation:
"""


# ---------------------------------
# Import Libraries
import os
import sys
import time
import traceback

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, f"{DJED_ROOT}/src"]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)


from utils.assets_db import AssetsDB
from utils.file_manager import FileManager

from utils.settings.style_rc import *


# ---------------------------------
# Variables
db = AssetsDB()

DJED_ROOT = os.getenv("DJED_ROOT")
Icons = f'{DJED_ROOT}/src/utils/resources/icons'

# ---------------------------------
# Start Here

class TextFeild(QWidget):
    def __init__(self, parent=None):
        super(TextFeild, self).__init__(parent)


        h_layout = QHBoxLayout(self)
        self.setLayout(h_layout)
        self.label = QLabel(self)
        self.line_edit = QLineEdit(self)

        h_layout.addWidget(self.label)
        h_layout.addWidget(self.line_edit)
        # h_layout.addItem(QSpacerItem(100, 2, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum))




    def set_name(self, name):
        self.label.setText(name)

    def set_default_value(self, value):
        self.line_edit.setText(value)

    def set_tooltip(self, text):
        self.setToolTip(text)

    def set_placeholder(self, text):
        self.line_edit.setPlaceholderText(text)




class TreeItemWidget(QWidget):
    def __init__(self, widgets_data, parent=None):
        super(TreeItemWidget, self).__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.widgets = {}
        self.all_widgets()
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        if not widgets_data:
            return

        for i, item in enumerate(widgets_data):
            if isinstance(item, dict):
                continue
            item_data = widgets_data.get(item)
            widget_type = item_data.get("type")
            widget_class = self.widgets.get(widget_type)
            if not widget_class:
                continue
            widget = self.widgets.get(widget_type)(self)
            widget.set_name(item_data.get("name"))

            widget.set_default_value(str(item_data.get("default_value")))
            widget.set_placeholder(str(item_data.get("placeholder")))
            widget.set_tooltip(str(item_data.get("tool_tip")))

            self.main_layout.addWidget(widget)



    def all_widgets(self):
        # input text
        self.widgets["input_text"] = TextFeild


class ItemRoles():
    TapName = Qt.UserRole+10
    SettingName = Qt.UserRole+11
    SettingFields = Qt.UserRole+12


class StyledItemDelegate(QStyledItemDelegate):
    def __init__(self, _index=None, parent=None):
        super(StyledItemDelegate, self).__init__(parent)
        self._index = _index


    def paint(self, painter, option, index):
        if (index == self._index):
            if isinstance(option.widget, QAbstractItemView):
                option.widget.openPersistentEditor(index)
        else:
            super(StyledItemDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        if (index == self._index):
            tap_name = index.parent().data(ItemRoles.TapName)
            ui_fields = index.data(ItemRoles.SettingFields)

            editor = TreeItemWidget(ui_fields, parent=parent)

            editor.installEventFilter(self)
            return editor
        return super(StyledItemDelegate, self).createEditor(parent, option, index)


    # def setEditorData(self, editor, index):
    #     if not index.isValid(): return
    #     if self.model_indices and index in self.model_indices:
    #         txt = index.model().data(index, Qt.EditRole)
    #         if isinstance(txt, str):
    #             editor.setText(txt)
    #     else:
    #         super().setEditorData(editor, index)


    # def setModelData(self, editor, model, index):
    #     if self.model_indices and index in self.model_indices:
    #         model.setData(index, editor.text(), Qt.EditRole)
    #     else:
    #         super().setModelData(editor, model, index)


    def updateEditorGeometry(self, editor, option, index):
        editor.setContentsMargins(0, 0, 0, 0)
        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        s = super(StyledItemDelegate, self).sizeHint(option, index)
        s.setHeight(s.height() * 1.5)
        return s


class SettingsTree(QTreeView):
    def __init__(self, parent=None):
        super(SettingsTree, self).__init__(parent)
        self.fm = FileManager()
        self.data_model = QStandardItemModel(0, 1)
        self.header().hide()
        self.setModel(self.data_model)

    def add_rows(self, items_data):
        # self.setItemDelegate(Delegate())
        for tap in items_data:
            tap_item = QStandardItem()
            tap_item.setText(tap)
            tap_item.setData(tap, ItemRoles.TapName)

            child = QStandardItem()
            tap_item.appendRow([child])

            children_items = items_data.get(tap)

            for item in children_items:
                child.setData(item, ItemRoles.SettingName)
                child.setData(children_items, ItemRoles.SettingFields)

                sub_children_items = children_items.get(item)

                if self.fm.dict_depth(sub_children_items) > 1:
                    drop_item = QStandardItem()
                    drop_item.setText(item)
                    tap_item.appendRow([drop_item])

                    sub_child = QStandardItem()
                    sub_child.setData(item, ItemRoles.SettingName)
                    sub_child.setData(sub_children_items, ItemRoles.SettingFields)
                    drop_item.appendRow([sub_child])

                    self.set_item_widget(drop_item, row=0)



            self.data_model.appendRow(tap_item)
            self.set_item_widget(tap_item, row=0)

    def set_item_widget(self, item, row=0):
        index = self.data_model.index(row, 0, self.data_model.indexFromItem(item))
        self.setItemDelegate(StyledItemDelegate(_index=index))
        self.openPersistentEditor(index)




class SettingsWindow(QMainWindow):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.init_win()
        self.color()

        self.fm = FileManager()
        ui_data = self.fm.read_json(r"settings.json")

        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)

        self.main_layout = QVBoxLayout()
        self.cw.setLayout(self.main_layout)

        # tree widget
        self.setting_tree = SettingsTree()
        self.setting_tree.add_rows(ui_data)

        # buttons
        l_btn = QHBoxLayout(self.cw)
        self.save_btn = QPushButton("Save")

        l_btn.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        l_btn.addWidget(self.save_btn)

        self.main_layout.addWidget(self.setting_tree)
        self.main_layout.addLayout(l_btn)



        # self.setting_table.expandAll()

    def init_win(self):
        title = "Djed Settings"
        icon_path = os.path.join(Icons, "settings.png")

        SizeObject = QGuiApplication.primaryScreen().availableGeometry()
        self.screen_height = SizeObject.height()
        self.screen_width = SizeObject.width()


        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(title)
        self.setMinimumSize(self.screen_width * 0.4, self.screen_height * 0.45)

        self.setStyleSheet(open("style.qss").read())
        self.font = QFont()
        self.font.setFamily("DejaVu Sans Condensed")
        self.font.setPointSize(20)
        self.font.setBold(True)
        self.font.setWeight(50)
        self.font.setKerning(True)

        self.setFont(self.font)

    def color(self):
        darkPalette = QPalette()
        color = QColor(45,45,45)
        display_color = QColor(127,127,127)
        darkPalette.setColor(QPalette.Window, color)

        # darkPalette.setColor(QPalette.WindowText, Qt.white)
        # darkPalette.setColor(QPalette.Base, QColor(18, 18, 18))
        # darkPalette.setColor(QPalette.AlternateBase, display_color)
        # darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
        # darkPalette.setColor(QPalette.ToolTipText, Qt.white)
        # darkPalette.setColor(QPalette.Text, Qt.white)
        # darkPalette.setColor(QPalette.Disabled, QPalette.Text, display_color)
        # darkPalette.setColor(QPalette.Button, color)
        # darkPalette.setColor(QPalette.ButtonText, Qt.white)
        # darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, display_color)
        # darkPalette.setColor(QPalette.BrightText, Qt.red)
        # darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
        #
        # darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        # darkPalette.setColor(QPalette.HighlightedText, Qt.black)
        # darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, display_color)

        self.setPalette(darkPalette)


# Main Function
def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    win = SettingsWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
