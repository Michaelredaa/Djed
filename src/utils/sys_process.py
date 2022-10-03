# -*- coding: utf-8 -*-
"""
Documentation:
"""

import os
import site
from pathlib import Path

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

