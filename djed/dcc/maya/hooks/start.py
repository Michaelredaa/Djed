# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))


def add_maya_module(maya_module_path=None):
    try:
        if maya_module_path is None:
            maya_module_path = Path.home().joinpath("Documents", "maya", "modules")
        else:
            maya_module_path = Path(str(maya_module_path))

        maya_module_path.mkdir(parents=True, exist_ok=True)
        mod_file = maya_module_path.joinpath("djed.mod")
        root_path = DJED_ROOT.joinpath('djed/dcc/maya/hooks/scripts').as_posix()
        cmd = f'+ Djed 1.0 {root_path}\nscripts: {root_path}'

        mod_file.unlink(missing_ok=True)

        with mod_file.open('w') as f:
            f.write(cmd)

        return "Done"
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    print(__name__)
