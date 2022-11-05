# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# import libraries
import sys
import os

from PySide2 import QtWidgets, QtGui, QtCore

DJED_ROOT = os.getenv('DJED_ROOT')

class Message(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(open(f"{DJED_ROOT}/src/utils/resources/stylesheet.qss").read())


    def event(self, event):
        if event.type() in (event.LayoutRequest, event.Resize):
            if event.type() == event.Resize:
                res = super().event(event)
            else:
                res = False
            details = self.findChild(QtWidgets.QTextEdit)
            if details:
                details.setMaximumSize(16777215, 16777215)

            self.setMinimumWidth(320)
            self.setMaximumSize(16777215, 16777215)
            return res
        return super().event(event)

# ---------------------------------
def text_dialog(parent=None):
    inp = QtWidgets.QInputDialog(parent)

    inp.setStyleSheet(open(f"{DJED_ROOT}/src/utils/resources/stylesheet.qss").read())

    ##### SOME SETTINGS
    inp.setInputMode(QtWidgets.QInputDialog.TextInput)
    #inp.setFixedSize(400, 200)
    #inp.setOption(QtWidgets.QInputDialog.UsePlainTextEditForTextInput)
    # p = inp.palette()
    # p.setColor(inp.backgroundRole(), QtCore.Qt.red)
    # inp.setPalette(p)

    inp.setWindowTitle('Save Backup')
    inp.setLabelText('Comment:')
    #####

    if inp.exec_() == QtWidgets.QDialog.Accepted:
        print(inp.textValue())
    else:
        print('cancel')
    inp.deleteLater()

    return inp.textValue()


def save_dialog(parent=None, ext = "Files (*.png *.exr)"):
    filenames = QtWidgets.QFileDialog.getSaveFileName( parent, 'Save File As', '', ext)
    return filenames[0]

def message(parent=None, title="Error", message=""):

    #msg = QtWidgets.QMessageBox()
    msg = Message()
    if parent:
        msg = QtWidgets.QMessageBox(parent)
    if title == "Error":
        msg.setIcon(QtWidgets.QMessageBox.Critical)
    elif title == "Info":
        msg.setIcon(QtWidgets.QMessageBox.Information)

    elif title == "warning":
        msg.setIcon(QtWidgets.QMessageBox.Warning)

    msg.setText(title)
    msg.setInformativeText(message)
    msg.setWindowTitle(title)

    msg.exec_()
    return msg

def info(parent=None, message=""):
    msg = Message()
    msg.setIcon(QtWidgets.QMessageBox.Information)

    if parent:
        msg = QtWidgets.QMessageBox(parent)
    msg.setWindowTitle("Info")
    msg.setText(message)
    msg.exec_()



def browse_dirs(parent=None, title="Select a directory", base_dir=""):
    return QtWidgets.QFileDialog.getExistingDirectory(parent, title, base_dir)

def browse_files(parent=None, title="Select a file", base_dir="", filters=".*", use_native=True):

    return QtWidgets.QFileDialog.getOpenFileName(parent, title, base_dir, filters)[0]

# Main function
def main():
    pass


if __name__ == '__main__':
    
    main()
    
