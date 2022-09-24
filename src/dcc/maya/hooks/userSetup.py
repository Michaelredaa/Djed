# >>>>>>>>>
# Djed Tools
# Add self
import pathlib

import maya.cmds as cmds


def open_commandPort():
    if not cmds.commandPort(":4436", query=True):
        cmds.commandPort(name=":4436", sourceType="python")


def init_djed():
    import traceback
    import os
    import sys
    import site
    from pathlib import Path

    DJED_ROOT = Path(os.getenv('DJED_ROOT'))

    print('Djed: ', DJED_ROOT)
    try:
        site.addsitedir(DJED_ROOT.joinpath('venv/python39/Lib/site-packages').as_posix())
        sys.path.append(DJED_ROOT.joinpath('src').as_posix())
        sys.path.append(DJED_ROOT.joinpath('src/dcc/maya/hooks').as_posix())

        print('start DJED')
        import shelf
        shelf.main()
        open_commandPort()


    except:
        print(traceback.format_exc())

cmds.evalDeferred("init_djed()")
# <<<<<<<<<