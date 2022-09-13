# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import time
from pathlib import Path

DJED_ROOT = Path(os.getenv('DJED_ROOT'))

from PySide2.QtWidgets import QMessageBox

from utils.spp_remote import RemotePainter
from utils.dialogs import message
from utils.sys_process import is_process_running, execute_commmand
from utils.file_manager import FileManager

fm = FileManager()


def connect_spp():
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
        message(None, 'Error', 'Can not get the current session of substance painter.')


def process(instance):
    asset_name = instance.get('name')
    data = instance.get('data')

    colorspace = data.get("colorspace", "aces")
    sgs = data.get('data')

    mesh_path = data.get('mesh_path', '')
    cfg = data.get('cfg', {})

    spp_exe = Path(fm.get_cfg('spp')['spp_exe']).parent

    if not spp_exe:
        message(None, 'Error', 'Please configure the substance painter executable first.')
        return

    args = [str(spp_exe), '--enable-remote-scripting']
    execute_commmand(*args)

    wait_until(open_spp_file, 90, period=0.25, mesh_path=mesh_path, cfg=cfg)


def wait_until(somepredicate, timeout, period=0.25, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if somepredicate(**kwargs): return True
        time.sleep(period)
    return False


def open_spp_file(mesh_path, project_path=None, cfg=None, *args):
    spp_exe = Path(fm.get_cfg('spp')['spp_exe']).parent

    if is_process_running(str(spp_exe)):
        sp = connect_spp()

        if sp:
            print("connected to substance")
            cmd = ''
            cmd += 'import sys, os\n'
            cmd += 'sys.path.append(os.path.join(os.getenv("DJED_ROOT"), "src"))'
            cmd += 'from dcc.spp.api.pipeline import create_project'
            cmd += f'create_project(mesh_file={mesh_path}, project_path={project_path}, cfg={cfg})'

            try:
                result = eval(sp.execScript(cmd, 'python'))
            except NameError:
                pass

            return True


def update_spp(mesh_path, current_sbp_path=None, udim=True):
    sp = connect_spp()

    if (not current_sbp_path) and sp:
        current_sbp_path = eval(sp.execScript('substance_painter.project.file_path()', 'python'))
    else:
        message(None, 'Error', 'Can not get the current session of substance painter.')

    update_mesh_file = DJED_ROOT.joinpath('Scripts/dcc/Substance/api/update_mesh.py')

    print(current_sbp_path)
    data = {'path': mesh_path}

    cmd_text = "print('## Djed Tools ##')\n"
    cmd_text += "import sys\n"
    cmd_text += f"data={data}\n"
    cmd_text += f"sys.argv = [data, ]\n"
    cmd_text += f"with open(r'{update_mesh_file}', 'r') as f:\n"
    cmd_text += "\texec(f.read())\n"

    sp.execScript(cmd_text, 'python')


# TODO
def update_substance(self, mesh_path, current_sbp_path=None, udim=True):
    sp = self.substance_connect()

    if (not current_sbp_path) and sp:
        current_sbp_path = eval(sp.execScript('substance_painter.project.file_path()', 'python'))
    else:
        QMessageBox(None, 'Error', 'Can not get the current session of substance painter.')

    update_mesh_file = DJED_ROOT.joinpath('Scripts/dcc/Substance/api/update_mesh.py')

    print(current_sbp_path)
    data = {'path': mesh_path}

    cmd_text = "print('## Djed Tools ##')\n"
    cmd_text += "import sys\n"
    cmd_text += f"data={data}\n"
    cmd_text += f"sys.argv = [data, ]\n"
    cmd_text += f"with open(r'{update_mesh_file}', 'r') as f:\n"
    cmd_text += "\texec(f.read())\n"

    sp.execScript(cmd_text, 'python')


# Main function
def main():
    pass


if __name__ == '__main__':
    print(__name__)
