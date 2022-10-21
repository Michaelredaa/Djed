# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import os
import sys
from cx_Freeze import setup, Executable

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, DJED_ROOT + '/src']
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from version import version

# ---------------------------------
# Variables

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable("start.py", base="", targetName=base, icon=f"{DJED_ROOT}/src/utils/resources/icons/djed.png")
]

build_options = {
    "include_files": ["docs", "src", "venv", "README.md"],
    "packages": ["sqlite3", "pyblish", "pyblish-maya", "PySide2", "psutil"]
}

# ---------------------------------
# Start Here


setup(
    name="Djed",
    version=version,
    description="Djed tools for 3d asset management",
    options={"build_exe": build_options},
    executables=executables
)
