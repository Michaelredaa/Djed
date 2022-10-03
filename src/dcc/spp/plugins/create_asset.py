# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))

from utils.spp_remote import RemotePainter
from utils.dialogs import message
from src.utils.sys_process import is_process_running, execute_commmand
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
        print("mesh_path", mesh_path)
        if is_process_running(spp_exe.name):
            sp = self.connect_spp()
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

    def connect_spp(self):
        """
        To connect with the current substance painter session
        :return: substance painter object
        """
        try:
            sp = RemotePainter()
            sp.checkConnection()
            sp.execScript('import substance_painter', 'python')
            sp.execScript('[Djed]', 'python')
            return sp
        except:
            pass
            # print(traceback.format_exc())
            # message(None, 'Error', 'Can not get the current session of substance painter.')


if __name__ == '__main__':
    print(__name__)
