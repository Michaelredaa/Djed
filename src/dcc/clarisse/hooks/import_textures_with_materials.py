# -*- coding: utf-8 -*-
"""
Documentation: 
"""


# ---------------------------------
# Import Libraries
import os
import sys
from pathlib import Path

import ix

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.joinpath('src').as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from dcc.clarisse.plugins.create_material_from_textures import CreateMaterialFromTextures
from dcc.clarisse.plugins.load_asset import LoadAsset

import pyblish.api
import pyblish.util

# ---------------------------------
# Variables


# ---------------------------------
# Start Here
def process():
    tex_dir = ix.api.GuiWidget.open_folder(ix.application)

    if not tex_dir:
        return

    colorspace = "aces"
    to_renderer = 'standardSurface'

    context = pyblish.api.Context()
    instance_obj = CreateMaterialFromTextures(
        tex_dir,
        colorspace=colorspace,
        to_renderer=to_renderer,
        context="selected",
    )
    instance = instance_obj.process(context)
    LoadAsset().process(instance)


# Main Function
def main():
    process()


if __name__ == '__main__':
    main()
