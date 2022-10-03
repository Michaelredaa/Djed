# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))

from dcc.spp.api.pipeline import connect_spp
from utils.dialogs import message
from src.utils.sys_process import is_process_running
from utils.file_manager import FileManager
from utils.generic import wait_until

import pyblish.api

fm = FileManager()


class createAsset(pyblish.api.InstancePlugin):
    label = "create project and set the asset"
    order = pyblish.api.ExtractorOrder
    hosts = ["spp"]
    families = ["asset"]

    trying_depth = 3

    def process(self, instance):
        asset_name = instance.name
        data = instance.data

        colorspace = data.get("colorspace", "aces")
        mesh_path = data.get('mesh_path', '')
        cfg = data.get('cfg', )

        spp_exe = fm.get_cfg('spp')['spp_exe']

        if not spp_exe:
            message(None, 'Error', 'Please configure the substance painter executable first.')
            return

        # args = [str(spp_exe), '--enable-remote-scripting']
        # execute_commmand(*args)

        open_flag = wait_until(self.open_spp_file, 90, period=0.25, mesh_path=mesh_path, cfg=cfg)
        if open_flag:
            self.open_spp_file(mesh_path, project_path=None, cfg=None)
        else:
            self.trying_depth -= 1
            self.process(instance)

    def open_spp_file(self, mesh_path, project_path=None, cfg=None, *args):
        spp_exe = Path(fm.get_cfg('spp')['spp_exe'])
        if is_process_running(spp_exe.name):
            sp = connect_spp()
            if sp:
                print("connected to substance")
                cmd = 'import sys, os\n'
                cmd += 'sys.path.append(os.path.join(os.getenv("DJED_ROOT"), "src"))\n'
                cmd += 'from dcc.spp.api.pipeline import create_project\n'
                cmd += f'create_project(r"{mesh_path}", project_path=r"{project_path}", cfg={cfg})\n'
                cmd += 'print("Done")\n'

                try:
                    result = eval(sp.execScript(cmd, 'python'))
                except NameError:
                    pass

                return True

        return False



if __name__ == '__main__':
    print(__name__)
