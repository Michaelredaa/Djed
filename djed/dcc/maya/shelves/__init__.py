# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# import libraries
import os
import sys

import importlib
import traceback
from pathlib import Path
from itertools import groupby

import maya.cmds as cmds
import maya.mel as mel

# ---------------------------------
shelf_name = "Djed"

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
icons = DJED_ROOT.joinpath('djed/utils/resources/icons')
shelves_dir = DJED_ROOT.joinpath('djed/dcc/maya/shelves')

sysPaths = [DJED_ROOT.as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.utils.logger import Logger
from djed.settings.settings import get_value

log = Logger(
    name="Maya Shelf",
    use_file=get_value("enable_logger", "general", "settings", "enable_logger").get("value")
)


def delete_self():
    if cmds.shelfLayout(shelf_name, ex=True):
        # mel.eval('deleteShelfTab '+shelf_name)
        cmds.deleteUI(shelf_name)
        gShelfTopLevel = mel.eval('$tmpVar=$gShelfTopLevel')
        cmds.saveAllShelves(gShelfTopLevel)


def get_modules():
    """
    TO get all buttons modules and return sorted and grouped by order
    :return: list(list(modules))
    """

    modules = []
    for btn_file in shelves_dir.iterdir():
        if btn_file.name.endswith(".py") and "__" not in btn_file.name:
            try:
                spec = importlib.util.spec_from_file_location(btn_file.stem, btn_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'djed_order'):
                    modules.append(module)
            except Exception as e:
                log.error(f"Error loading module: {btn_file}, \n{e}")
                log.error(traceback.format_exc())

    modules.sort(key=lambda x: x.djed_order)

    return [list(g) for k, g in groupby(modules, lambda x: int(x.djed_order))]


def create_self():
    # Delete old shelves
    try:
        delete_self()
    except:
        pass

    shelftoplevel = mel.eval("$gShelfTopLevel = $gShelfTopLevel;")
    shelves = cmds.tabLayout(shelftoplevel, query=True, childArray=True)

    # Add new shelves
    if not (shelf_name in shelves):
        mel.eval("addNewShelfTab {};".format(shelf_name))

    try:
        for btn in cmds.shelfLayout(shelf_name, q=1, ca=1):
            cmds.deleteUI(btn)
    except:
        pass

    log.info("Creating Buttons")
    for shelf_buttons in get_modules():
        for mod_btn in shelf_buttons:
            cmd_text = "## Djed Tools ##\n\n"
            cmd_text += f"from djed.dcc.maya.shelves import {mod_btn.__name__}\n"
            cmd_text += f"from importlib import reload; reload({mod_btn.__name__})\n"

            left_cmd = cmd_text + f"{mod_btn.__name__}.left_click()"
            right_cmd = cmd_text + f"{mod_btn.__name__}.right_click()"
            double_cmd = cmd_text + f"{mod_btn.__name__}.double_click()"

            btn_info = {
                "parent": shelf_name,
                "label": mod_btn.__name__,
                "annotation": mod_btn.djed_annotation,
                "image1": icons.joinpath(mod_btn.djed_icon).as_posix(),
                "imageOverlayLabel": mod_btn.djed_imgLabel,
                "overlayLabelColor": mod_btn.djed_color,
                "overlayLabelBackColor": mod_btn.djed_backColor,
                "command": left_cmd,
                "doubleClickCommand": double_cmd
                # noDefaultPopup=True
            }

            new_shelf_button = cmds.shelfButton(**btn_info)

        cmds.setParent(shelf_name)
        cmds.separator(width=12, height=35, style='shelf', hr=0)
        cmds.setParent(shelf_name)

    cmds.saveAllShelves(shelftoplevel)

    # if popupMenus:
    #     popup_menu = cmds.popupMenu(parent=new_shelf_button, button=n)
    #     for pop in popupMenus:
    #         menu_command = cmds.menuItem(label=pop["label"], sourceType=pop["sourceType"],
    #                                      parent=popup_menu, command=pop["command"])


# Main function
def main():
    log.info("Initialize Djed maya shelf")
    create_self()



if __name__ == '__main__':
    main()
