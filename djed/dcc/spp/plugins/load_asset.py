# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))

sysPaths = [DJED_ROOT]
for sysPath in sysPaths:
    if str(sysPath) not in sys.path:
        sys.path.append(str(sysPath))

from djed.dcc.spp.api.remote_connect import connect_spp
from djed.utils.dialogs import message
from djed.utils.sys_process import is_process_running, execute_commmand
from djed.utils.file_manager import FileManager, PathResolver
from djed.utils.generic import wait_until
from djed.settings.settings import get_dcc_cfg
from djed.utils.logger import Logger
from djed.utils.assets_db import AssetsDB

import pyblish.api

fm = FileManager()
db = AssetsDB()


class LoadAsset(pyblish.api.InstancePlugin):
    label = "create project and set the asset"
    order = pyblish.api.ExtractorOrder
    hosts = ["spp"]
    families = ["asset"]

    trying_depth = 3

    def __init__(self):
        self.log = Logger(
            name=self.hosts[0] + '-' + self.__class__.__name__,
            use_file=get_dcc_cfg('general', 'settings', 'enable_logger')
        )

    def process(self, instance):

        self.log.debug(f"Loading asset `{instance.name}` in substance painter...")

        if self.trying_depth == 0:
            return

        asset_name = instance.name
        data = instance.data
        self.log.debug(f"Loading data `{data}`")

        colorspace = data.get("colorspace", "aces")
        mesh_path = data['geo_paths'].get('obj_file')
        cfg = data.get('cfg', {})

        self.spp_exe = Path(get_dcc_cfg("substance_painter", "configuration", "executable"))
        self.log.debug(f"Open `{self.spp_exe}` with `{cfg}`")

        if not self.spp_exe:
            message(None, 'Error', 'Please configure the substance painter executable first.')
            return

        args = [str(self.spp_exe), '--enable-remote-scripting']
        self.log.debug(f"Execute `{args}`")
        execute_commmand(*args)

        # get project path
        assets_key = data.get('asset_keys', {})
        assets_key['step'] = 'surfacing'

        all_versions = db.get_versions(uuid=data['uuid'], table_name='workingFile')
        spp_version = db.dcc_workfile_version(all_versions, 'substance_painter')
        padding = int(get_dcc_cfg("general", "settings", "version_padding"))
        version = 'v' + str(spp_version).zfill(padding)
        assets_key['version'] = version

        project_path = PathResolver(get_dcc_cfg('general', 'path', 'work', 'work_file'))
        project_path.format(**assets_key)



        open_flag = wait_until(
            self.open_spp_file,
            timeout=90,
            period=0.25,
            mesh_path=mesh_path,
            project_path=str(project_path),
            cfg=cfg
        )

        if open_flag:
            pass
            # self.open_spp_file(mesh_path, project_path=None, cfg=cfg)
        else:
            self.trying_depth -= 1
            self.process(instance)

    def open_spp_file(self, mesh_path, project_path=None, cfg=None, *args):
        spp_exe = self.spp_exe
        if is_process_running(spp_exe.name):
            sp = connect_spp()
            if sp:
                self.log.debug(f"connected to substance painter..")
                cmd = 'import sys, os\n'
                cmd += 'sys.path.append(os.getenv("DJED_ROOT"))\n'
                cmd += 'from djed.dcc.spp.api.pipeline import create_project\n'
                cmd += f'create_project(r"{mesh_path}", project_path=r"{project_path}", cfg={cfg})\n'
                cmd += 'print("Done")\n'

                self.log.debug(f"Set command: ```{cmd}```")
                try:
                    result = eval(sp.execScript(cmd, 'python'))
                except NameError:
                    pass

                return True

        return False


if __name__ == '__main__':
    data = {'name': 'portal', 'family': 'asset', 'host': 'spp',
            'mesh_path': 'D:/3D/working/projects/Generic/03_Workflow/Assets/portal/Export/portal/v0022/portal.obj',
            'cfg': {'export_root': '../Export/$selection', 'default_texture_resolution': 512,
                    'normal_map_format': 'OpenGL',
                    'tangent_space_mode': 'PerVertex', 'project_workflow': 'TextureSetPerUVTile',
                    'import_cameras': False}}

    context = pyblish.api.Context()
    instance = context.create_instance(**data)
    LoadAsset().process(instance)

    print(__name__)
