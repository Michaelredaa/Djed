# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import sys
import re
import traceback
from functools import partial

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


# ---------------------------------
# Variables


# ---------------------------------
# Start Here
class ItemRoles():
    UUID = Qt.UserRole + 1
    AssetName = Qt.UserRole + 2
    AssetID = Qt.UserRole + 3
    Thumbnail = Qt.UserRole + 4
    CDate = Qt.UserRole + 5
    MDate = Qt.UserRole + 6
    OBJ = Qt.UserRole + 7
    USD = Qt.UserRole + 8
    ABC = Qt.UserRole + 9
    FBX = Qt.UserRole + 10
    MAYA = Qt.UserRole + 11
    SPP = Qt.UserRole + 12
    Tags = Qt.UserRole + 13
    Projects = Qt.UserRole + 14


def add_checkable_action(qmenu, name, checked=True):
    action = QWidgetAction(qmenu.parent())
    cb = QCheckBox(name)
    cb.setChecked(checked)
    action.setDefaultWidget(cb)
    qmenu.addAction(action)

    return cb

class AssetItemWidget(QWidget):
    def __init__(self, parent=None):
        super(AssetItemWidget, self).__init__(parent)

        self.setAutoFillBackground(True)
        self.label_text = "NewAsset"
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.DeferredDelete:
            print("QEvent.Type.DeferredDelete CustomItemWidget of:", self.label_text)

        return False

    def setData(self, role, value):
        if role == Qt.DisplayRole:
            self.label_text = value

    def paintEvent(self, event):
        painter = QPainter(self)

        # Default brush and pen
        bg_brush = QBrush(QColor("#8C8C8C"))
        pen = Qt.NoPen

        painter.save()
        painter.setPen(pen)
        painter.setBrush(bg_brush)
        painter.drawRoundedRect(self.rect(), 12, 12)
        painter.restore()

        # Paint the label text
        painter.save()
        painter.drawText(self.rect(), Qt.AlignCenter, self.label_text)
        painter.restore()


class CustomProxyFilter(QSortFilterProxyModel):

    def __init__(self):
        super(CustomProxyFilter, self).__init__()

        self.matched_string = ''
        self.search_filter = {'names': True, 'tags':True, 'projects':True}

    def is_match(self, names):

        string_list = str(self.matched_string).split(' ')
        for string in string_list:
            string = string.strip()
            if string == '':
                continue

            reg = re.compile(f'.*{string}.*')
            matching = list(filter(reg.search, names))
            if matching:
                return True

        return False

    def filterAcceptsRow(self, row, index):
        """Re-implementing built-in to hide columns wif non matches."""
        _index = self.sourceModel().index(row, 0)
        self.matched_string = self.filterRegExp().pattern().lower()
        if not self.matched_string:
            return True

        tags = _index.data(ItemRoles.Tags)
        projects = _index.data(ItemRoles.Projects)
        asset_name = _index.data(ItemRoles.AssetName)

        return (self.is_match([asset_name]) and self.search_filter.get('names')) \
               or (self.is_match(tags) and self.search_filter.get('tags')) \
               or (self.is_match(projects) and self.search_filter.get('projects'))


class ListView(QListView):
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.index = 100

        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setViewMode(QListView.IconMode)
        self.setMovement(QListView.Static)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # https://doc.qt.io/qt-6/qabstractitemview.html
        self.setEditTriggers(QAbstractItemView.EditKeyPressed)

        self.data_model = QStandardItemModel()
        # self.filter_model = QSortFilterProxyModel(self.data_model)
        self.filter_model = CustomProxyFilter()

        self.filter_model.setDynamicSortFilter(True)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_model.sort(1, Qt.AscendingOrder)

        self.filter_model.setSourceModel(self.data_model)
        self.setModel(self.filter_model)

        self.verticalScrollBar().valueChanged.connect(self.on_load_more)

    def set_timer(self, timer):
        self._timer = timer

    def addItem(self, item_data):
        item = AssetItem(item_data)
        self.data_model.appendRow(item)

        self.index -= 1
        if self.index < 0:
            if not self.verticalScrollBar().isVisible():
                self.index = 25
            else:
                self._timer.stop()

        filter_index = self.filter_model.mapFromSource(item.index())
        # self.list.setIndexWidget(filter_index, item.item_widget)
        return item

    def data_log(self):
        for row in range(self.filter_model.rowCount()):
            index = self.filter_model.index(row, 0)
            print("Current Item: ", index.data(), self.indexWidget(index))

    def on_load_more(self):
        self.index = 50
        self._timer.start()

    def dragMoveEvent(self, event):
        print('drag')
        # if event.mimeData().hasUrls():
        # event.accept()

    def dragEnterEvent(self, event):
        print('drop')
        # if event.mimeData().hasUrls():
        # event.accept()


class AssetItem(QStandardItem):
    def __init__(self, data):
        super(AssetItem, self).__init__()

        pixmap = QPixmap(data.get("thumb_path"))
        self.setIcon(QIcon(pixmap))
        self.setText(data.get("asset_name"))
        self.setData(data.get("uuid"), ItemRoles.UUID)
        self.setData(data.get("asset_name"), ItemRoles.AssetName)
        self.setData(data.get("thumb_path"), ItemRoles.Thumbnail)
        self.setData(data.get("asset_id"), ItemRoles.AssetID)
        self.setData(data.get("creation_date"), ItemRoles.CDate)
        self.setData(data.get("modification_date"), ItemRoles.MDate)
        self.setData(data.get("obj_path"), ItemRoles.OBJ)
        self.setData(data.get("usd_path"), ItemRoles.USD)
        self.setData(data.get("abc_path"), ItemRoles.ABC)
        self.setData(data.get("fbx_path"), ItemRoles.FBX)
        self.setData(data.get("ma_path"), ItemRoles.MAYA)
        self.setData(data.get("spp_path"), ItemRoles.SPP)
        self.setData(data.get("tags"), ItemRoles.Tags)
        self.setData(data.get("projects"), ItemRoles.Projects)


class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

        self.autocomplete_list = []
        self.completer = QCompleter()

        self.autocomplete_setup()


    def set_autocomplete_list(self, _list):
        self.autocomplete_list = _list
        self.autocomplete_setup()

    def autocomplete_setup(self):
        complete_model = QStringListModel()
        complete_model.setStringList(self.autocomplete_list)

        self.completer.setModel(complete_model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
        QLineEdit.keyPressEvent(self, event)




class WScreenShot(QWidget):

    isClosed = Signal(bool)

    @classmethod
    def run(cls):
        cls.win = cls()
        cls.win.show()

    def __init__(self, parent=None, path=None):
        super(WScreenShot, self).__init__(parent)
        self.path = path
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet('''background-color:black; ''')
        self.setWindowOpacity(0.6)
        desktopRect = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(desktopRect)
        self.setCursor(Qt.CrossCursor)
        self.blackMask = QBitmap(desktopRect.size())
        self.blackMask.fill(Qt.black)
        self.mask = self.blackMask.copy()
        self.isDrawing = False
        self.startPoint = QPoint()
        self.endPoint = QPoint()


    def paintEvent(self, event):
        if self.isDrawing:
            self.mask = self.blackMask.copy()
            pp = QPainter(self.mask)
            pen = QPen()
            pen.setStyle(Qt.NoPen)
            pp.setPen(pen)
            brush = QBrush(Qt.white)
            pp.setBrush(brush)
            pp.drawRect(QRect(self.startPoint, self.endPoint))
            self.setMask(QBitmap(self.mask))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPoint = event.pos()
            self.endPoint = self.startPoint
            self.isDrawing = True
        else:
            self.isDrawing = False

    def mouseMoveEvent(self, event):
        if self.isDrawing:
            self.endPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.RightButton:
            self.close()

        if event.button() == Qt.LeftButton:
            try:
                self.endPoint = event.pos()
                screenshot = QGuiApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
                rect = QRect(self.startPoint, self.endPoint)
                outputRegion = screenshot.copy(rect)
                outputRegion.save(self.path, format='jpg', quality=100)
                self.isClosed.emit(True)
                self.close()
            except:
                QMessageBox.warning(self, "Error", traceback.format_exc())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


# Main Function
def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    thumb_path = r"D:\3D\working\projects\Generic\03_Workflow\Assets\Abagora\Scenefiles\mod\Modeling\Export\foo.jpg"
    screenshot = WScreenShot(path=thumb_path)
    screenshot.setWindowModality(Qt.ApplicationModal)
    screenshot.run()

    app.exec_()
    sys.exit()

if __name__ == '__main__':
    
    main()
    
