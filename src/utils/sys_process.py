# -*- coding: utf-8 -*-
"""
Documentation:
"""

import os
import tempfile
import subprocess
from pathlib import Path

from ctypes import windll



def is_process_running(process_name):
    """
    Check if there is any running process that contains the given name processName.
    """
    # Use the tasklist command to get a list of all running processes
    tasklist = subprocess.Popen('tasklist', stdout=subprocess.PIPE).stdout.read().decode('utf-8')

    # Iterate over the lines and check if the process name is in any of them
    for line in tasklist.split('\n'):
        if process_name.lower()[:25] in line.lower():
            return True

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


if __name__ == '__main__':
    name = 'Adobe Substance 3D Painter'
    print(is_process_running(name))
