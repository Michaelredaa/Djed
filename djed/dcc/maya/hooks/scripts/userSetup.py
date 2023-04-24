# >>>>>>>>>
# Djed Tools
# Add self

import maya.cmds as cmds


def open_djed_commandPort():
    if not cmds.commandPort(":4436", query=True):
        cmds.commandPort(name=":4436", sourceType="python")


def init_djed():
    import traceback
    import os
    import sys
    import site
    from pathlib import Path

    DJED_ROOT = Path(os.getenv('DJED_ROOT'))

    print('[Djed] Root: ', DJED_ROOT.as_posix())
    try:
        sys.path.insert(0, DJED_ROOT.as_posix())
        site.addsitedir(DJED_ROOT.joinpath('venv/python/Lib/site-packages').as_posix())

        from djed.dcc.maya import shelves as djed_shelves
        djed_shelves.main()
        open_djed_commandPort()

        # from dcc.maya.api.lib import set_project_event
        # set_project_event()

    except:
        print(traceback.format_exc())

cmds.evalDeferred("init_djed()")
# <<<<<<<<<