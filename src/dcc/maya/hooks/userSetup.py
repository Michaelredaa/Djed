# -*- coding: utf-8 -*-
import maya.cmds as cmds

cmds.evalDeferred("initPlugin()")


def initPlugin():
    import traceback
    import os
    import sys
    import site

    try:
        site.addsitedir(os.path.join(os.getenv('DJED_ROOT'), 'venv/python39/Lib/site-packages'))
        sys.path.append(os.path.join(os.getenv('DJED_ROOT'), 'src/dcc/maya/hooks'))

        import shelf
        shelf.main()
        print('start DJED')

    except:
        print(traceback.format_exc())