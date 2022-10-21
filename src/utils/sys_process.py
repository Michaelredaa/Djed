# -*- coding: utf-8 -*-
"""
Documentation:
"""

import os
import site
import tempfile
from pathlib import Path

from ctypes import windll

DJED_ROOT = Path(os.getenv('DJED_ROOT'))

site.addsitedir(DJED_ROOT.joinpath('venv/python39/Lib/site-packages').as_posix())

import subprocess
import psutil


def is_process_running(process_name):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over teh all teh running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def execute_commmand(*args):
    subprocess.Popen(args)


def create_shortcut(shortcut_path, target, arguments='', working_dir=''):
    shortcut_path = Path(shortcut_path)
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)

    def escape_path(path):
        return str(path).replace('\\', '/')

    js_content = f'''
        var sh = WScript.CreateObject("WScript.Shell");
        var shortcut = sh.CreateShortcut("{escape_path(shortcut_path)}");
        shortcut.TargetPath = "{escape_path(target)}";
        shortcut.Arguments = "{arguments}";
        shortcut.WorkingDirectory = "{working_dir}";
        shortcut.Save();'''

    fd, path = tempfile.mkstemp('.js')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(js_content)
        subprocess.run([r'wscript.exe', path])
    finally:
        os.unlink(path)


def run_as_administrator(cmd):
    """
    to run a cmd command as administrator
    :param cmd: the command text
    :return:
    """
    result = windll.shell32.ShellExecuteW(
        None,  # handle to parent window
        'runas',  # verb
        'cmd.exe',  # file on which verb acts
        ' '.join(['/c', str(cmd)]),  # parameters
        None,  # working directory (default is cwd)
        0,  # show window normally
    )
    success = result > 32
    return success
