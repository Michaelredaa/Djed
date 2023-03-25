# >>>>>>>>>
# Djed Tools
# Add self

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

    print('Djed: ', DJED_ROOT.as_posix())
    try:
        site.addsitedir(DJED_ROOT.joinpath('venv/python39/Lib/site-packages').as_posix())
        sys.path.append(DJED_ROOT.joinpath('djed').as_posix())
        sys.path.append(DJED_ROOT.joinpath('djed/dcc/maya/hooks').as_posix())

        print('start DJED')
        from dcc.maya import shelves
        shelves.main()
        open_commandPort()

        from dcc.maya.api.lib import set_project_event
        set_project_event()

    except:
        print(traceback.format_exc())

cmds.evalDeferred("init_djed()")
# <<<<<<<<<