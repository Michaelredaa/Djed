#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import os
import sys
import json
from collections import OrderedDict

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, f"{DJED_ROOT}/src"]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.assets_db import AssetsDB
from utils.file_manager import FileManager

from utils.resources.style_rc import *
from utils.resources.style_rc import *

# ---------------------------------
# Variables
db = AssetsDB()


# ---------------------------------
# Start Here

class TextFiled(QWidget):
    name = 'input_text'

    def __init__(self, parent=None):
        super(TextFiled, self).__init__(parent)

        h_layout = QHBoxLayout(self)
        self.setLayout(h_layout)
        self.label = QLabel(self)
        self.line_edit = QLineEdit(self)

        h_layout.addWidget(self.label)
        h_layout.addWidget(self.line_edit)
        # h_layout.addItem(QSpacerItem(100, 2, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum))

    def set_name(self, name):
        # name = ' '.join(str(name).split('_')).title()
        self.label.setText(name)

    def set_default_value(self, value):
        self.line_edit.setText(value)

    def set_tooltip(self, text):
        self.setToolTip(text)

    def set_placeholder(self, text):
        self.line_edit.setPlaceholderText(text)


class MultiTextFiled(QWidget):
    def __init__(self, parent=None, num=2):
        super(MultiTextFiled, self).__init__(parent)

        h_layout = QHBoxLayout(self)
        self.setLayout(h_layout)

        self.line_edits = {}
        for i in range(num):
            label = QLabel(self)
            line_edit = QLineEdit(self)
            self.line_edits[i] = {
                'label': label,
                'lineedit': line_edit
            }

            h_layout.addWidget(label)
            h_layout.addWidget(line_edit)
        # h_layout.addItem(QSpacerItem(100, 2, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum))

    def set_name(self, name, num=0):
        # name = ' '.join(str(name).split('_')).title()
        self.line_edits[num]['label'].setText(name)

    def set_default_value(self, value, num=1):
        self.line_edits[num]['lineedit'].setText(value)

    def set_tooltip(self, text, num=0):
        self.line_edits[num]['lineedit'].setToolTip(text)

    def set_placeholder(self, text, num=0):
        self.line_edits[num]['lineedit'].setPlaceholderText(text)


class TableField(QWidget):
    name = 'table_field'

    def __init__(self, parent=None):
        super(TableField, self).__init__(parent=parent)

        g_layout = QGridLayout(self)
        self.setLayout(g_layout)

        self.table = QTableWidget()
        # self.table.setAlternatingRowColors(True)
        self.table.setCornerButtonEnabled(False)
        self.table.setFrameStyle(QFrame.NoFrame)

        g_layout.addWidget(self.table)

    def set_data(self, data):
        hor_headers = []

        self.table.setRowCount(len(data))
        for r, item_data in enumerate(data):
            vert_headers = []
            hor_headers.append(item_data.get('label'))

            self.table.setColumnCount(len(item_data.get('value', {})))

            c = 0
            for col, value in item_data.get('value', {}).items():
                vert_headers.append(col)
                new_item = QTableWidgetItem(value)
                new_item.setToolTip(value)
                self.table.setItem(r, c, new_item)
                c += 1

            self.table.setHorizontalHeaderLabels(vert_headers)

        self.table.setVerticalHeaderLabels(hor_headers)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        #
        # self.adjustSize()

        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # +++


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

        if isinstance(widgets_data, dict):
            widgets_data = [widgets_data]

        for item in widgets_data:
            if not isinstance(item, dict):
                continue

            widget_type = item.get("type")
            if not widget_type:
                return

            widget_class = self.widgets.get(widget_type)
            if not widget_class:
                continue

            if 'multi' in widget_type:
                widget = QWidget(self)
                h_layout = QHBoxLayout(self)
                widget.setLayout(h_layout)

                for i in range(len(item.get("label"))):
                    in_widget = self.widgets.get(widget_type)(self)
                    in_widget.set_name(item.get("label")[i])

                    in_widget.set_default_value(str(item.get("default_value")[i]))
                    in_widget.set_placeholder(str(item.get("placeholder")[i]))
                    in_widget.set_tooltip(str(item.get("tooltip")[i]))
                    h_layout.addWidget(in_widget)

            elif 'table_field' in widget_type:
                widget = self.widgets.get(widget_type)(self)
                widget.set_data(item.get('data', []))

            else:

                widget = self.widgets.get(widget_type)(self)
                widget.set_name(item.get("label"))

                widget.set_default_value(str(item.get("default_value")))
                widget.set_placeholder(str(item.get("placeholder")))
                widget.set_tooltip(str(item.get("tooltip")))

            self.main_layout.addWidget(widget)

    def all_widgets(self):
        # input text
        self.widgets["input_text"] = TextFiled
        self.widgets["multi_input_text"] = TextFiled
        self.widgets["table_field"] = TableField


class ItemRoles():
    TapName = Qt.UserRole + 10
    SettingName = Qt.UserRole + 11
    SettingFields = Qt.UserRole + 12


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

    def has_childrens(self, data):
        for item in data:
            if 'children' in item:
                return True
        return False

    def has_refernce(self, data):
        for item in data:
            if isinstance(item, str) and ('$' in item):
                return True
        return False

    def populate_row(self, widgets_data, parent_item):
        widgets_item = QStandardItem()
        parent_item.appendRow([widgets_item])
        widgets_item.setData(widgets_data, ItemRoles.SettingFields)
        self.set_item_widget(parent_item, row=0)

    def populate_rows(self, data, row_item, row=None):

        if self.has_refernce(data):
            for i in range(len(data)):
                if "$" in data[i]:
                    file_name = data[i].split('$')[-1]
                    cfg_path = f"./cfg/{file_name}.json"

                    if not os.path.isfile(cfg_path):
                        continue

                    with open(cfg_path) as f:
                        data_list = json.load(f, object_pairs_hook=OrderedDict)
                        data_list[data[i]] = os.path.abspath(cfg_path)
                        data.pop(i)
                        data.insert(i, data_list)


        if not self.has_childrens(data):
            self.populate_row(data, row_item)

        for child_data in data:
            if 'children' in child_data:
                child_item = QStandardItem()
                child_item.setText(child_data.get('label'))
                child_item.setData(child_data.get('label'), ItemRoles.TapName)
                child_item.setData(child_data, ItemRoles.SettingFields)
                if row:
                    row_item.insertRow(row, [child_item])
                else:
                    row_item.appendRow([child_item])
                self.populate_rows(child_data.get('children'), child_item)

    def add_rows(self, items_data):
        # self.setItemDelegate(Delegate())
        # for tap in items_data:
        #     tap_item = QStandardItem()
        #     tap_item.setText(tap)
        #     tap_item.setData(tap, ItemRoles.TapName)
        #
        #     child = QStandardItem()
        #     tap_item.appendRow([child])
        #
        #     children_items = items_data.get(tap)
        #
        #     for item in children_items:
        #         child.setData(item, ItemRoles.SettingName)
        #         child.setData(children_items, ItemRoles.SettingFields)
        #
        #         sub_children_items = children_items.get(item)
        #
        #         if self.fm.dict_depth(sub_children_items) > 1:
        #             drop_item = QStandardItem()
        #             drop_item.setText(item)
        #             tap_item.appendRow([drop_item])
        #
        #             sub_child = QStandardItem()
        #             sub_child.setData(item, ItemRoles.SettingName)
        #             sub_child.setData(sub_children_items, ItemRoles.SettingFields)
        #             drop_item.appendRow([sub_child])
        #
        #             self.set_item_widget(drop_item, row=0)
        #
        #
        #
        #     self.data_model.appendRow(tap_item)
        #     self.set_item_widget(tap_item, row=0)

        for row_data in items_data:
            row_item = QStandardItem()
            row_item.setText(row_data.get('label'))
            row_item.setData(row_data.get('name'), ItemRoles.TapName)
            row_item.setData(row_data, ItemRoles.SettingFields)

            children_data = row_data.get('children', [])

            self.populate_rows(children_data, row_item)

            self.data_model.appendRow(row_item)
            self.set_item_widget(row_item, row=0)

    def set_item_widget(self, item, row=0):
        index = self.data_model.index(row, 0, self.data_model.indexFromItem(item))
        self.setItemDelegate(StyledItemDelegate(_index=index))
        self.openPersistentEditor(index)


class SettingsWindow(QMainWindow):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.init_win()
        self.color()

        self.connect_events()

        self.setting_tree.expandAll()

    def connect_events(self):

        self.save_btn.clicked.connect(self.on_save)

        self.setting_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setting_tree.customContextMenuRequested.connect(self.on_right_click)

        self.mousePressEvent = self.showEvent

    def init_win(self):
        title = "Djed Settings"

        Size_object = QGuiApplication.primaryScreen().availableGeometry()
        screen_height = Size_object.height()
        screen_width = Size_object.width()

        self.setWindowIcon(QIcon(":icons/settings.png"))
        self.setWindowTitle(title)
        self.setMinimumSize(screen_width * 0.45, screen_height * 0.5)

        self.setStyleSheet(open(f"{DJED_ROOT}/src/utils/resources/stylesheet.qss").read())

        # set Font
        font = QFont()
        font.setFamily("DejaVu Sans Condensed")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(50)
        font.setKerning(True)

        # setFont(self.font)

        # Update table
        with open(f"{DJED_ROOT}/src/settings/cfg/settings.json") as f:
            ui_data = json.load(f, object_pairs_hook=OrderedDict)

        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)

        self.main_layout = QVBoxLayout()
        self.cw.setLayout(self.main_layout)

        # tree widget
        self.setting_tree = SettingsTree()
        self.setting_tree.add_rows(ui_data.get('items', []))

        # buttons
        l_btn = QHBoxLayout(self.cw)
        self.save_btn = QPushButton("Save")

        l_btn.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        l_btn.addWidget(self.save_btn)

        self.main_layout.addWidget(self.setting_tree)
        self.main_layout.addLayout(l_btn)

    def color(self):
        darkPalette = QPalette()
        color = QColor(45, 45, 45)
        display_color = QColor(127, 127, 127)
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

    def on_right_click(self, point):

        index = self.setting_tree.indexAt(point)

        if not index.isValid():
            return

        # We build the menu.
        menu = QMenu()
        duplicate_action = menu.addAction("Duplicate")
        print_action = menu.addAction("Print Data")

        duplicate_action.triggered.connect(lambda: self.on_duplicate_item(index))
        print_action.triggered.connect(lambda: self.on_print_data(index))

        menu.exec_(self.setting_tree.mapToGlobal(point))

    def on_duplicate_item(self, index):
        item = self.setting_tree.data_model.itemFromIndex(index)
        parent = item.parent()
        data = index.data(ItemRoles.SettingFields)

        self.setting_tree.populate_rows([data], parent, item.row() + 1)

    def on_print_data(self, index):

        item = self.setting_tree.data_model.itemFromIndex(index)

        item_data = index.data(ItemRoles.SettingFields)
        parent_data = index.parent().data(ItemRoles.SettingFields)

        print('item data : ', item_data)
        print('parent data : ', parent_data)

    def on_save(self):

        for x in self.iterItems(self.setting_tree.data_model.invisibleRootItem()):
            if not x:
                continue

            print(x.data(ItemRoles.TapName), x.data(ItemRoles.SettingFields))

    def iterItems(self, root):
        if root is not None:
            for row in range(root.rowCount()):
                row_item = root.child(row, 0)
                yield row_item
                # if row_item.hasChildren():
                #     for childIndex in range(row_item.rowCount()):
                #         child = row_item.child(childIndex, 0)
                #         yield child

    def showEvent(self, event):
        self.show

    def closeEvent(self, event):
        self.destroy()

    def mousePressEvent(self, event):
        pass


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
    main()
