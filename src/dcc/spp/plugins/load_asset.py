# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
from pathlib import Path



DJED_ROOT = Path(os.getenv('DJED_ROOT'))

sysPaths = [DJED_ROOT, DJED_ROOT.joinpath('src')]
for sysPath in sysPaths:
    if str(sysPath) not in sys.path:
        sys.path.append(str(sysPath))

from dcc.spp.api.remote_connect import connect_spp
from utils.dialogs import message
from src.utils.sys_process import is_process_running, execute_commmand
from utils.file_manager import FileManager
from utils.generic import wait_until
from settings.settings import get_dcc_cfg

import pyblish.api

fm = FileManager()


class LoadAsset(pyblish.api.InstancePlugin):
    label = "create project and set the asset"
    order = pyblish.api.ExtractorOrder
    hosts = ["spp"]
    families = ["asset"]

    trying_depth = 3

    def process(self, instance):
        if self.trying_depth == 0:
            return
        asset_name = instance.name
        data = instance.data

        colorspace = data.get("colorspace", "aces")
        mesh_path = data.get('mesh_path', '')
        cfg = data.get('cfg', {})

        spp_exe = get_dcc_cfg("substance_painter", "configuration", "executable")

        if not spp_exe:
            message(None, 'Error', 'Please configure the substance painter executable first.')
            return

        args = [str(spp_exe), '--enable-remote-scripting']
        execute_commmand(*args)

        open_flag = wait_until(self.open_spp_file, 90, period=0.25, mesh_path=mesh_path, cfg=cfg)
        if open_flag:
            pass
            # self.open_spp_file(mesh_path, project_path=None, cfg=cfg)
        else:
            self.trying_depth -= 1
            self.process(instance)

    def open_spp_file(self, mesh_path, project_path=None, cfg=None, *args):
        spp_exe = Path(get_dcc_cfg("substance_painter", "configuration", "executable"))
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
    data = {'name': 'portal', 'family': 'asset', 'host': 'spp',
     'mesh_path': 'D:/3D/working/projects/Generic/03_Workflow/Assets/portal/Export/portal/v0022/portal.obj',
     'cfg': {'export_root': '../Export/$selection', 'default_texture_resolution': 512, 'normal_map_format': 'OpenGL',
             'tangent_space_mode': 'PerVertex', 'project_workflow': 'TextureSetPerUVTile', 'import_cameras': False}}

    context = pyblish.api.Context()
    instance = context.create_instance(**data)
    LoadAsset().process(instance)


    print(__name__)
