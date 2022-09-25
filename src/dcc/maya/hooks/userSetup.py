# >>>>>>>>>
# Djed Tools
# Add self
import pathlib

import maya.cmds as cmds


def open_commandPort():
    if not cmds.commandPort(":4436", query=True):
        cmds.commandPort(name=":4436", sourceType="python")

def register_plugins():
    from pathlib import Path
    import os
    import pyblish.api
    import pyblish.util

    DJED_ROOT = Path(os.getenv('DJED_ROOT'))

    plugin_path = DJED_ROOT.joinpath('src/dcc/maya/plugin')
    pyblish.util.plugin.deregister_all_plugins()
    pyblish.api.deregister_plugin_path(plugin_path.as_posix())
    pyblish.api.register_plugin_path(plugin_path.as_posix())



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