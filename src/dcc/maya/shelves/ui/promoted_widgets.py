# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# import libraries
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# ---------------------------------
class EditableLabel(QWidget):
    """Editable label"""
    textChanged = Signal(str)

    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent=parent)

        self.is_editable = kwargs.get("editable", True)
        self.keyPressHandler = KeyPressHandler(self)

        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setObjectName("mainLayout")

        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.mainLayout.addWidget(self.label)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.mainLayout.addWidget(self.lineEdit)
        # hide the line edit initially
        self.lineEdit.setHidden(True)

        # setup signals
        self.create_signals()

    def create_signals(self):
        self.lineEdit.installEventFilter(self.keyPressHandler)
        self.label.mousePressEvent = self.labelPressedEvent

        # give the lineEdit both a `returnPressed` and `escapedPressed` action
        self.keyPressHandler.escapePressed.connect(self.escapePressedAction)
        self.keyPressHandler.returnPressed.connect(self.returnPressedAction)

    def text(self):
        """Standard QLabel text getter"""
        return self.label.text()

    def setText(self, text):
        """Standard QLabel text setter"""
        self.label.blockSignals(True)
        self.label.setText(text)
        self.label.blockSignals(False)

    def labelPressedEvent(self, event):
        """Set editable if the left mouse button is clicked"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setLabelEditableAction()

    def setLabelEditableAction(self):
        """Action to make the widget editable"""
        if not self.is_editable:
            return

        self.label.setHidden(True)
        self.label.blockSignals(True)
        self.lineEdit.setHidden(False)
        self.lineEdit.setText(self.label.text())
        self.lineEdit.blockSignals(False)
        self.lineEdit.setFocus(Qt.MouseFocusReason)
        self.lineEdit.selectAll()

    def labelUpdatedAction(self):
        """Indicates the widget text has been updated"""
        text_to_update = self.lineEdit.text()

        if text_to_update != self.label.text():
            self.label.setText(text_to_update)
            self.textChanged.emit(text_to_update)

        self.label.setHidden(False)
        self.lineEdit.setHidden(True)
        self.lineEdit.blockSignals(True)
        self.label.blockSignals(False)

    def returnPressedAction(self):
        """Return/enter event handler"""
        self.labelUpdatedAction()

    def escapePressedAction(self):
        """Escape event handler"""
        self.label.setHidden(False)
        self.lineEdit.setHidden(True)
        self.lineEdit.blockSignals(True)
        self.label.blockSignals(False)

class KeyPressHandler(QObject):
    """Custom key press handler"""
    escapePressed = Signal(bool)
    returnPressed = Signal(bool)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            event_key = event.key()
            if event_key == Qt.Key_Escape:
                self.escapePressed.emit(True)
                return True
            if event_key == Qt.Key_Return or event_key == Qt.Key_Enter:
                self.returnPressed.emit(True)
                return True

        return QObject.eventFilter(self, obj, event)

class ClickedLabel(QLabel):
    rightClicked = Signal()
    leftClicked = Signal()
    doubleClicked = Signal()

    # def __init__(self, parent=None):
    #
    #     super(QLabel, self).__init__(parent)

    def mousePressEvent(self, event):
        self.last = "Click"
        if event.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit()
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftClicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.last = "DClick"

    def mouseReleaseEvent(self, event):
        if self.last == "DClick":
            self.doubleClicked.emit()
            self.update()
        self.last = "RClick"


    # def mousePressEvent(self, event):
    #     self.clicked.emit()
    #     QLabel.mousePressEvent(self, Qt.MouseButton.LeftButton)

class EditableLabelWidget(QWidget):
    """Sample Widget"""

    def __init__(self, parent=None, **kwargs):
        super(EditableLabelWidget, self).__init__(parent)

        # create the editable label
        self.label = EditableLabel(self)
        self.label2 = ClickedLabel(self)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.label2)
        self.setLayout(self.mainLayout)

        self.label.setText("click me to edit")
        self.label2.setText("click me left/right")
        self.setWindowTitle("Editable Label")

        # connect our custom signal
        self.label.textChanged.connect(self.labelTextChangedAction)
        self.label2.rightClicked.connect(self.labelRightClick)
        self.label2.leftClicked.connect(self.labelLeftClick)

    def labelTextChangedAction(self, text):
        print("# label updated: \"{0}\"".format(text))

    def labelLeftClick(self):
        print("Left Click")

    def labelRightClick(self):
        print("Right Click")

class Completer(QCompleter):

    def __init__(self, parent=None):
        super(Completer, self).__init__(parent)

        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setWrapAround(False)

    # Add texts instead of replace
    def pathFromIndex(self, index):
        path = QCompleter.pathFromIndex(self, index)

        lst = str(self.widget().text()).split('/')

        if len(lst) > 1:
            path = '%s/%s' % ('/'.join(lst[:-1]), path)

        return path

    # Add operator to separate between texts
    def splitPath(self, path):
        path = str(path.split('/')[-1]).lstrip(' ')
        return [path]

