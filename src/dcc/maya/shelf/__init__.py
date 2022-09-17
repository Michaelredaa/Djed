# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# import libraries
import sys, os
from collections import OrderedDict

import maya.cmds as cmds
import maya.mel as mel

# ---------------------------------
shelf_name = "Djed"
__python__ = sys.version_info[0]

DJED_ROOT = os.getenv("DJED_ROOT")
icons = os.path.join(DJED_ROOT, "Scripts", "Utils", "Resources", "icons").replace("\\", "/")

btns_data = OrderedDict()

btns_data["Export Mesh"] = {
    "annotation": "Export selected geometry",
    "image1": icons + "/exportMesh.png",
    "imageOverlayLabel": "",
    "overlayLabelColor": (0.9, 0.9, 0.9),
    "overlayLabelBackColor": (0.0, 0.0, 0.0, 0.0),
    "command": """
import os
import sys
import importlib

DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
dcc = os.path.join(DJED_ROOT, "Scripts", "dcc")

sysPathes = [DJED_ROOT, scripts, dcc]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)
import Maya
import Maya.Maya_Functions
import Linker

from Maya.Renderer import Arnold as arnold
from Maya.Maya_Functions import Maya

ma_fn = Maya(arnold)
export_mesh = ma_fn.export_selection(["obj", "abc"])[0]

""",
    "popupMenu": []
}

# Substance painter
btns_data["separator"] = {}

btns_data["Send SPP"] = {
    "annotation": "Send selection to substance painter",
    "image1": icons + "/sendSubstace.png",
    "imageOverlayLabel": "",
    "overlayLabelColor": (0.9, 0.9, 0.9),
    "overlayLabelBackColor": (0.0, 0.0, 0.0, 0.0),
    "command": """
import os
import sys
import importlib

DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
dcc = os.path.join(DJED_ROOT, "Scripts", "dcc")

sysPathes = [DJED_ROOT, scripts, dcc]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)
import Maya
import Maya.Maya_Functions
import Linker

importlib.reload(Maya)
importlib.reload(Linker)
importlib.reload(Maya.Maya_Functions)

from Maya.Renderer import Arnold as arnold
from Maya.Maya_Functions import Maya
from Linker import Linker


ma_fn = Maya(arnold)
export_mesh = ma_fn.export_selection(["obj", "abc"])[0]
lk = Linker(ma_fn)
lk.to_substance(export_mesh)

""",
    "popupMenu": []
}

btns_data["Update SPP"] = {
    "annotation": "Update selection to substance painter current session",
    "image1": icons + "/updateSubstance.png",
    "imageOverlayLabel": "",
    "overlayLabelColor": (0.9, 0.9, 0.9),
    "overlayLabelBackColor": (0.0, 0.0, 0.0, 0.0),
    "command": """
import os
import sys
import importlib

DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
dcc = os.path.join(DJED_ROOT, "Scripts", "dcc")

sysPathes = [DJED_ROOT, scripts, dcc]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)
import Maya
import Maya.Maya_Functions
import Linker

from Maya.Renderer import Arnold as arnold
from Maya.Maya_Functions import Maya
from Linker import Linker


ma_fn = Maya(arnold)
export_mesh = ma_fn.export_selection(["obj", "abc"])[0]
lk = Linker(ma_fn)
lk.update_substance(export_mesh, current_sbp_path=None)

""",
    "popupMenu": []

}

btns_data["Update Existence SPP"] = {
    "annotation": "Update selection to substance painter already existence file",
    "image1": icons + "/updateExistSubstance.png",
    "imageOverlayLabel": "",
    "overlayLabelColor": (0.9, 0.9, 0.9),
    "overlayLabelBackColor": (0.0, 0.0, 0.0, 0.0),
    "command": """
import os
import sys
import importlib

DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
dcc = os.path.join(DJED_ROOT, "Scripts", "dcc")

sysPathes = [DJED_ROOT, scripts, dcc]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)

import Maya.Maya_Functions
import Linker

from Maya.Renderer import Arnold as arnold
from Maya.Maya_Functions import Maya
from Linker import Linker


spp_file = cmds.fileDialog2(fileFilter="*.spp", ds=2,fm=1, okc="select")

if spp_file:
    spp_file = spp_file[0]
else:
    spp_file = ""

ma_fn = Maya(arnold)
export_mesh = ma_fn.export_selection(["obj", "abc"])[0]
lk = Linker(ma_fn)
lk.update_substance(export_mesh, current_sbp_path=spp_file)    

""",
    "popupMenu": []

}

# Clarisse
btns_data["separator"] = {}

btns_data["Send Clarisse"] = {
    "annotation": "Send selection to clarisse",
    "image1": icons + "/sendClarisse.png",
    "imageOverlayLabel": "",
    "overlayLabelColor": (0.9, 0.9, 0.9),
    "overlayLabelBackColor": (0.0, 0.0, 0.0, 0.0),
    "command": """

import os
import importlib

DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
dcc = os.path.join(DJED_ROOT, "Scripts", "dcc", "Clarisse")

sysPathes = [DJED_ROOT, scripts, dcc]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)


import Maya  
import Linker
import Maya.Maya_Functions


import Maya.Maya_Functions

from Maya.Renderer import Arnold as arnold
from Maya.Maya_Functions import Maya

import Clarisse_Functions as csf
importlib.reload(csf)


m = Maya("")
mayaData = m.send_to_clarisse()

cls = csf.Clarisse()
cls.maya_to_clarisse(mayaData)

""",
    "popupMenu": []
}

# Maya
btns_data["separator"] = {}

btns_data["Create MTL with Tex"] = {
    "annotation": "Send selection to clarisse",
    "image1": icons + "/sendClarisse.png",
    "imageOverlayLabel": "",
    "overlayLabelColor": (0.9, 0.9, 0.9),
    "overlayLabelBackColor": (0.0, 0.0, 0.0, 0.0),
    "command": """

import os
import importlib

DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
dcc = os.path.join(DJED_ROOT, "Scripts", "dcc", "Clarisse")

sysPathes = [DJED_ROOT, scripts, dcc]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)


import Maya  
import Linker
import Maya.Maya_Functions


import Maya.Maya_Functions

from Maya.Renderer import Arnold as arnold
from Maya.Maya_Functions import Maya

import Clarisse_Functions as csf
importlib.reload(csf)


m = Maya("")
mayaData = m.send_to_clarisse()

cls = csf.Clarisse()
cls.maya_to_clarisse(mayaData)

""",
    "popupMenu": []
}

btns_data["Create Material"] = {
    "annotation": "Send selection to clarisse",
    "image1": icons + "/sendClarisse.png",
    "imageOverlayLabel": "",
    "overlayLabelColor": (0.9, 0.9, 0.9),
    "overlayLabelBackColor": (0.0, 0.0, 0.0, 0.0),
    "command": """

import os
import importlib

DJED_ROOT = os.getenv("DJED_ROOT")
scripts = os.path.join(DJED_ROOT, "Scripts")
dcc = os.path.join(DJED_ROOT, "Scripts", "dcc", "Clarisse")

sysPathes = [DJED_ROOT, scripts, dcc]

for sysPath in sysPathes:
    if not sysPath in sys.path:
        sys.path.append(sysPath)


import Maya  
import Linker
import Maya.Maya_Functions


import Maya.Maya_Functions

from Maya.Renderer import Arnold as arnold
from Maya.Maya_Functions import Maya

import Clarisse_Functions as csf
importlib.reload(csf)


m = Maya("")
mayaData = m.send_to_clarisse()

cls = csf.Clarisse()
cls.maya_to_clarisse(mayaData)

""",
    "popupMenu": []
}


def create_self():
    try:
        delete_self()
    except:
        pass
    shelftoplevel = mel.eval("$gShelfTopLevel = $gShelfTopLevel;")
    shelves = cmds.tabLayout(shelftoplevel, query=True, childArray=True)

    if not (shelf_name in shelves):
        mel.eval("addNewShelfTab {};".format(shelf_name))

    try:
        for btn in cmds.shelfLayout(shelf_name, q=1, ca=1):
            cmds.deleteUI(btn)
    except:
        pass

    for new_btn in btns_data:
        # create shelf
        if new_btn == "separator":
            cmds.setParent(shelf_name)
            cmds.separator(width=12, height=35, style='shelf', hr=0)
            continue

        new_shelf_button = cmds.shelfButton(parent=shelf_name,
                                            annotation=btns_data[new_btn]["annotation"],
                                            image1=btns_data[new_btn]["image1"],
                                            command=btns_data[new_btn]["command"],
                                            imageOverlayLabel=btns_data[new_btn]["imageOverlayLabel"],
                                            label=new_btn,
                                            overlayLabelColor=btns_data[new_btn]["overlayLabelColor"],
                                            overlayLabelBackColor=btns_data[new_btn]["overlayLabelBackColor"],
                                            # noDefaultPopup=True
                                            )

        popupMenus = btns_data[new_btn]["popupMenu"]
        n = len(popupMenus)
        if popupMenus:
            popup_menu = cmds.popupMenu(parent=new_shelf_button, button=n)
            for pop in popupMenus:
                menu_command = cmds.menuItem(label=pop["label"], sourceType=pop["sourceType"],
                                             parent=popup_menu, command=pop["command"])
        cmds.saveAllShelves(shelftoplevel)


def delete_self():
    if cmds.shelfLayout(shelf_name, ex=True):
        # mel.eval('deleteShelfTab '+shelf_name)
        cmds.deleteUI(shelf_name)
        gShelfTopLevel = mel.eval('$tmpVar=$gShelfTopLevel')
        cmds.saveAllShelves(gShelfTopLevel)


# Main function
def main():
    create_self()


if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
