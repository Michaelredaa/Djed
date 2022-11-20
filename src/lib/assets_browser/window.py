# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import os
import sys
from pathlib import Path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.assets_db import AssetsDB
from utils.file_manager import FileManager
from utils.dialogs import browse_files
from settings.settings import get_dcc_cfg, get_textures_settings

from lib.assets_browser.ui.promoted_widgets import ItemRoles, WScreenShot, add_checkable_action
from lib.assets_browser.ui import Ui_AssetBrowserWindow, Ui_addTagWidget

from utils.resources.style_rc import *
from utils.resources.stylesheet import get_stylesheet

# ---------------------------------
# Variables

db = AssetsDB()


# ---------------------------------
# Start Here

class AddTagWindow(QWidget, Ui_addTagWidget):
    def __init__(self, tags, parent=None):
        super(AddTagWindow, self).__init__(parent)
        self.setupUi(self)

        self.tags = [] if (tags is None) else tags
        self.row = 0
        self.col = 0

        self.init_ui()
        self.connect_events()

    def init_ui(self):
        self.setWindowTitle('Add Tags')
        self.setWindowIcon(QIcon(":/icons/tags.png"))

        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowModality(Qt.WindowModal)

        for tag in self.tags:
            self.add_tag_to_bar(tag)

    def connect_events(self):
        self.le_tags.returnPressed.connect(self.create_tags)
        self.le_tags.completer.activated.connect(self.create_tags)
        # self.cb_project.stateChanged.connect(self.on_tag_type_change)

        self.pb_close.clicked.connect(self.close)

    def create_tags(self):
        new_tag = self.le_tags.text().strip()

        if new_tag and (new_tag not in self.tags):
            self.tags.append(new_tag)
            self.add_tag_to_bar(new_tag)

    def add_tag_to_bar(self, text):
        tag = QFrame()
        tag.setStyleSheet('border:1px solid rgb(120, 120, 120); border-radius: 5px;')
        tag.setContentsMargins(2, 2, 2, 2)
        # tag.setFixedHeight(28)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(4, 4, 4, 4)
        hbox.setSpacing(10)
        tag.setLayout(hbox)
        label = QLabel(text)
        label.setStyleSheet('border:0px')
        label.setFixedHeight(16)
        hbox.addWidget(label)
        x_button = QPushButton('x')
        # x_button.setFixedSize(20, 20)

        x_button.setStyleSheet('''
        QPushButton{
            text-align: top;
            background-color: #4C3F3A;
            border: 0px solid #704020;
            padding: 0px 0px 0px 0px;
            margin: 0px 1px 0px 0px;
            border-radius: 5px;
            min-width: 14px;
            min-height: 14px;
            }
            
        QPushButton:hover,
        QPushButton:focus {
            color: black;
            background-color: #F3400F;
            border-color: #704020;
        }
            
        ''')
        x_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        x_button.clicked.connect(lambda: self.remove_tag_from_bar(text))
        hbox.addWidget(x_button)
        tag.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.l_tags.addWidget(tag)

        self.l_tags.addWidget(tag, self.row, self.col % 5, 1, 1)
        self.col += 1
        if self.col % 5 == 0:
            self.row += 1

        self.le_tags.setFocus()
        self.le_tags.setText("")

    def remove_tag_from_bar(self, tag_name):
        self.tags.remove(tag_name)

        for i in range(self.l_tags.count()):
            frame = self.l_tags.itemAt(i).widget()
            label = frame.children()[1]
            if label.text().strip() == tag_name:
                frame.setParent(None)
                break

    def reset_tags(self):
        self.row = 0
        self.col = 0
        for i in reversed(range(self.l_tags.count())):
            frame = self.l_tags.itemAt(i).widget()
            frame.setParent(None)

    def on_tag_type_change(self):
        self.reset_tags()


class AssetViewWindow(QMainWindow, Ui_AssetBrowserWindow):
    IconSize = 170

    def __init__(self, parent=None):
        super(AssetViewWindow, self).__init__(parent)
        self.setupUi(self)
        self.fm = FileManager()
        self.tags_win = None

        self.setStyleSheet(get_stylesheet())

        self.init_win()
        self.connect_events()

        self.populate_items()

    def init_win(self):
        title = "Asset Browser"

        # border colors
        darkPalette = QPalette()
        color = QColor(45, 45, 45)
        darkPalette.setColor(QPalette.Window, color)
        self.setPalette(darkPalette)

        SizeObject = QGuiApplication.primaryScreen().availableGeometry()
        self.screen_height = SizeObject.height()
        self.screen_width = SizeObject.width()

        self.setWindowIcon(QIcon(":/icons/djed.png"))
        self.setWindowTitle(title)
        self.setMinimumSize(self.screen_width * 0.4, self.screen_height * 0.3)
        self.showMaximized()

        # button

        # filter checkbox menu
        self.filter_menu = QMenu(self)
        self.filter_menu.setMinimumWidth(100)

        self.all_filter_cb = add_checkable_action(self.filter_menu, 'Select All', False)
        self.none_filter_cb = add_checkable_action(self.filter_menu, 'Unselect All', False)
        self.filter_menu.addSeparator()

        self.names_filter_cb = add_checkable_action(self.filter_menu, 'names', True)
        self.tags_filter_cb = add_checkable_action(self.filter_menu, 'tags', True)
        self.projects_filter_cb = add_checkable_action(self.filter_menu, 'projects', True)
        self.on_filter_changed()

        # list view
        self.lw_assets.setIconSize(QSize(AssetViewWindow.IconSize, AssetViewWindow.IconSize))
        self.lw_assets.setSpacing(10)

        #  slider
        self.horizontalSlider.setRange(AssetViewWindow.IconSize / 2, AssetViewWindow.IconSize * 2)
        self.horizontalSlider.setValue(AssetViewWindow.IconSize)
        self.horizontalSlider.setMinimumWidth(30)

        # table
        self.table_data.setHeaderLabels(["Select to preview"])

        # actions

    def connect_events(self):
        # search lineedit
        self.le_search.textChanged.connect(self.lw_assets.filter_model.setFilterRegExp)
        self.le_search.keyPressEvent = self.search_bar_key_event

        # list view
        self.lw_assets.doubleClicked.connect(self.on_item_double_clicked)
        self.lw_assets.selectionModel().selectionChanged.connect(self.on_item_selection_changed)

        # context menu
        self.lw_assets.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lw_assets.customContextMenuRequested.connect(self.on_asset_rt_clicked)

        # slider
        self.horizontalSlider.valueChanged.connect(self.on_change_icon_size)

        # buttons
        self.pushButton_filterItems.clicked.connect(self.on_filter_click)
        self.pushButton_refreshView.clicked.connect(self.refresh)

        # check box
        self.all_filter_cb.stateChanged.connect(self.on_filter_changed)
        self.none_filter_cb.stateChanged.connect(self.on_filter_changed)
        self.names_filter_cb.stateChanged.connect(self.on_filter_changed)
        self.tags_filter_cb.stateChanged.connect(self.on_filter_changed)
        self.projects_filter_cb.stateChanged.connect(self.on_filter_changed)

    def populate_items(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.add_item())
        self.timer.start(50)
        self.lw_assets.set_timer(self.timer)

        database_data = db.get_assets_data()

        self.img_iter = iter(database_data)

    def add_item(self):
        try:
            row = next(self.img_iter)

            thumb_path = db.get_thumbnail(asset_name=row[1], latest=True)
            if not (thumb_path or os.path.isfile(str(thumb_path))):
                thumb_path = ":/icons/empty_asset.png"
            item_data = {
                "asset_id": row[0],
                "asset_name": row[1],
                "creation_date": row[2],
                "modification_date": row[3],
                "uuid": row[4],
                "obj_path": row[7],
                "usd_path": row[8],
                "abc_path": row[9],
                "fbx_path": row[10],
                "ma_path": row[11],
                "spp_path": row[12],
                "thumb_path": thumb_path,
                "tags": db.get_tags(asset_name=row[1]),
                "projects": db.get_projects(asset_name=row[1])

            }

            item = self.lw_assets.addItem(item_data)

        except StopIteration:
            self.timer.stop()

    def on_text_changed(self):
        text = self.le_search.text()
        self.lw_assets.filter_model.setFilterWildcard("*" + text + "*")

    def on_change_icon_size(self):
        size = self.horizontalSlider.value()
        self.lw_assets.setIconSize(QSize(size, size))

        if not self.lw_assets.verticalScrollBar().isVisible():
            self.add_item()

    def on_item_double_clicked(self, index):
        print(index.data(ItemRoles.Thumbnail))
        print(index.data(ItemRoles.Tags))

    def on_item_selection_changed(self, item):
        indexes = item.indexes()
        if indexes:
            index = indexes[0]
            # thumbnail
            thum_path = index.data(ItemRoles.Thumbnail)
            self.pixmap_preview = QPixmap(thum_path)
            self.pixmap_preview = self.pixmap_preview.scaled(QSize(1024, 1024), Qt.KeepAspectRatio,
                                                             Qt.SmoothTransformation)
            self.label_preview0.setPixmap(self.pixmap_preview)
            self.label_preview0.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.label_preview0.setMargin(10)
            self.label_preview0.installEventFilter(self)

            # table data
            self.table_data.clear()
            self.table_data.setColumnCount(1)
            self.table_data.header().hide()  # setHeaderLabels([""])

            assset_name_item = QTreeWidgetItem([index.data(ItemRoles.AssetName)])

            # Tags
            tag_item = QTreeWidgetItem(["Tags"])
            for tag in index.data(ItemRoles.Tags):
                tag_child = QTreeWidgetItem([tag])
                tag_child.setFlags(tag_item.flags() | Qt.ItemIsEditable)
                tag_item.addChild(tag_child)

            # projects
            project_item = QTreeWidgetItem(["Projects"])
            for project in index.data(ItemRoles.Projects):
                project_child = QTreeWidgetItem([project])
                project_child.setFlags(tag_item.flags() | Qt.ItemIsEditable)
                project_item.addChild(project_child)

            # Geometry
            geos_item = QTreeWidgetItem(["Geometry"])
            geo_data = {
                "obj": ItemRoles.OBJ,
                "usd": ItemRoles.USD,
                "abc": ItemRoles.ABC,
                "fbx": ItemRoles.FBX,
            }

            for _type in geo_data:
                type_item = QTreeWidgetItem([_type])
                value = index.data(geo_data.get(_type))
                if not value:
                    continue
                geo_child = QTreeWidgetItem([value])
                type_item.addChild(geo_child)
                geos_item.addChild(type_item)

            # Source files
            source_item = QTreeWidgetItem(["Source Files"])
            source_data = {
                "maya": ItemRoles.MAYA,
                "Substance Painter": ItemRoles.SPP,
            }

            for _type in source_data:
                type_item = QTreeWidgetItem([_type])
                value = index.data(source_data.get(_type))
                if not value:
                    continue
                src_child = QTreeWidgetItem([value])
                type_item.addChild(src_child)
                source_item.addChild(type_item)

            # Date time
            date_item = QTreeWidgetItem(["Date time"])
            date_data = {
                "Modified": ItemRoles.MDate,
                "Created": ItemRoles.CDate,
            }

            for _type in date_data:
                value = index.data(date_data.get(_type))
                type_item = QTreeWidgetItem([_type + ": " + value])
                date_item.addChild(type_item)

            self.table_data.addTopLevelItem(assset_name_item)
            self.table_data.addTopLevelItem(tag_item)
            self.table_data.addTopLevelItem(project_item)
            self.table_data.addTopLevelItem(geos_item)
            self.table_data.addTopLevelItem(source_item)
            self.table_data.addTopLevelItem(date_item)

            # self.table_data.expandAll()
            tag_item.setExpanded(True)
            project_item.setExpanded(True)
            date_item.setExpanded(True)

    def search_bar_key_event(self, event):
        if event.key() == Qt.Key_Escape:
            self.le_search.clear()
        QLineEdit.keyPressEvent(self.le_search, event)

    def on_asset_rt_clicked(self):
        menu = QMenu(self)
        selection = self.lw_assets.selectionModel().selectedRows()
        if selection:
            send_action = menu.addMenu("Send to")
            send_to_maya_action = send_action.addAction("Maya")
            send_to_clarisse_action = send_action.addAction("Clarisse")
            # send_to_spp_action = send_action.addAction("Substance Painter")

            edit_action = menu.addAction("Edit asset")

            tag_action = menu.addAction("tags")
            change_thumb_action = menu.addAction("Change thumbnail")
            capture_thumb_action = menu.addAction("Capture screen thumbnail")

            # signals
            send_to_maya_action.triggered.connect(self.on_open_maya)
            send_to_clarisse_action.triggered.connect(self.on_open_clarisse)
            # send_to_spp_action.triggered.connect(self.on_open_spp)
            tag_action.triggered.connect(self.on_add_tag_window)
            edit_action.triggered.connect(self.on_edit_asset)

            change_thumb_action.triggered.connect(self.on_change_thumbnail)
            capture_thumb_action.triggered.connect(self.on_capture_thumbnail)

        else:
            refresh_action = menu.addAction("Refresh")

            # signals
            refresh_action.triggered.connect(self.refresh)

        cursor = QCursor()
        menu.exec_(cursor.pos())

    def on_open_maya(self):
        from dcc.linker.to_maya import send_to_maya

        index = self.get_selection()

        geo_path = index.data(ItemRoles.ABC)
        asset_name = index.data(ItemRoles.AssetName)
        asset_uuid = index.data(ItemRoles.UUID)

        asset = db.get_asset(uuid=asset_uuid)

        asset['family'] = 'asset'
        asset['colorspace'] = 'aces'
        asset['to_renderer'] = 'arnold'
        asset['geo_type'] = 'abc_file'
        asset['import_type'] = 'Import Geometry'

        send_to_maya(asset)

    def on_open_clarisse(self):
        from dcc.linker.to_clarisse import send_to_clarisse

        # get selection data
        index = self.get_selection()
        asset_uuid = index.data(ItemRoles.UUID)
        asset = db.get_asset(uuid=asset_uuid)

        asset['family'] = 'asset'
        asset['colorspace'] = 'aces'
        asset['to_renderer'] = 'autodesk_standard_surface'
        asset['geometry_type'] = 'abc_bundle'

        send_to_clarisse(asset)

    def on_open_spp(self):
        print("spp")

    def on_edit_asset(self):
        print("edit asset")

    def on_add_tag_window(self):
        index = self.get_selection()
        tags = index.data(ItemRoles.Tags)
        self.tags_win = AddTagWindow(tags, self)

        self.tags_win.index = index
        self.tags_win.le_tags.set_autocomplete_list(db.all_tags())

        self.tags_win.pb_add_tag.clicked.connect(lambda: self.on_add_tag(self.tags_win))
        self.tags_win.cb_project.stateChanged.connect(lambda: self.on_add_tag(self.tags_win, switch=True))

        self.tags_win.show()

    def on_add_tag(self, tags_win, switch=None):
        if switch:
            tags_win.reset_tags()
            if tags_win.cb_project.isChecked():
                tags_win.tags = tags_win.index.data(ItemRoles.Projects)
                tags_win.le_tags.set_autocomplete_list(db.all_projects())
            else:
                tags_win.tags = tags_win.index.data(ItemRoles.Tags)
                tags_win.le_tags.set_autocomplete_list(db.all_tags())

            tags_win.init_ui()
        else:
            new_tags = tags_win.tags

            if tags_win.cb_project.isChecked():
                db.delete_asset_projects(asset_id=tags_win.index.data(ItemRoles.AssetID))

                for project_name in new_tags:
                    db.add_project(asset_name=tags_win.index.data(ItemRoles.AssetName), project_name=project_name)
            else:
                db.delete_asset_tags(asset_id=tags_win.index.data(ItemRoles.AssetID))
                for tag_name in new_tags:
                    db.add_tag(asset_name=tags_win.index.data(ItemRoles.AssetName), tag_name=tag_name)

            self.refresh()
            tags_win.close()

    def on_change_thumbnail(self):
        index = self.get_selection()

        geo_path = index.data(ItemRoles.OBJ)
        if not geo_path:
            geo_path = ""

        tex_extensions = get_textures_settings("extensions")
        _filter = " ".join(["*." + x for x in tex_extensions])

        new_thumb = browse_files(self, "Select thumbnail", os.path.dirname(geo_path), f"Images ({_filter})")
        if not new_thumb:
            return
        db.set_thumbnail(asset_id=index.data(ItemRoles.AssetID), thumb_path=new_thumb)

        self.refresh()

    def on_capture_thumbnail(self):
        index = self.get_selection()
        geo_path = index.data(ItemRoles.OBJ)
        if not geo_path:
            geo_path = ""
        thumb_path = os.path.splitext(geo_path)[0] + ".jpg"
        self.screenshot = WScreenShot(path=thumb_path)
        self.screenshot.show()
        self.screenshot.setWindowModality(Qt.ApplicationModal)
        db.set_thumbnail(asset_id=index.data(ItemRoles.AssetID), thumb_path=thumb_path)
        self.refresh()

    def refresh(self):
        self.lw_assets.data_model.clear()
        self.populate_items()

    def select_item(self, index):
        self.lw_assets.selectionModel().setCurrentIndex(index, QItemSelectionModel.Current)
        self.lw_assets.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)

    def get_selection(self):
        indices = self.lw_assets.selectionModel().selectedRows()
        if not indices:
            return
        index = indices[0]
        return index

    def on_filter_click(self):
        cursor = QCursor()
        self.filter_menu.exec_(cursor.pos())

    def on_filter_changed(self):

        if self.all_filter_cb.isChecked():
            self.none_filter_cb.setChecked(False)
            self.names_filter_cb.setChecked(True)
            self.tags_filter_cb.setChecked(True)
            self.projects_filter_cb.setChecked(True)

        if self.none_filter_cb.isChecked():
            self.all_filter_cb.setChecked(False)
            self.names_filter_cb.setChecked(False)
            self.tags_filter_cb.setChecked(False)
            self.projects_filter_cb.setChecked(False)

        self.lw_assets.filter_model.search_filter = {
            'names': self.names_filter_cb.isChecked(),
            'tags': self.tags_filter_cb.isChecked(),
            'projects': self.projects_filter_cb.isChecked()
        }

    def closeEvent(self, event):
        if self.tags_win:
            self.tags_win.destroy()

        self.destroy()

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.Resize and widget is self.label_preview0:
            self.label_preview0.setPixmap(
                self.pixmap_preview.scaled(
                    self.label_preview0.width(),
                    self.label_preview0.height(),
                    Qt.KeepAspectRatio))
            return True
        return super(AssetViewWindow, self).eventFilter(widget, event)

# Main Function
def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    win = AssetViewWindow()
    # win = AddTagWindow(["gg", "ff"])
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
