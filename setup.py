# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import os
import sys
from cx_Freeze import setup, Executable
from pathlib import Path

DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix(), DJED_ROOT.joinpath('src').as_posix()]
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
    Executable("start.py", base=base, targetName="Djed", icon=f"{DJED_ROOT.as_posix()}/src/utils/resources/icons/djed.ico")
]

include_files = [
    "docs",
    "src",
    "venv",
    "start.py",
    "start.bat",
    "cfg.json",
    "README.md"
]

build_options = {
    "include_files": include_files,
    "packages": []
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
