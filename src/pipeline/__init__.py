#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# @Time : 9/17/2022
# @File : __init__.py

__version__ = "1.0.1"
__author__ = "Michael Reda"
__email__ = "eng.michaelreda@gmail.com"
__license__ = "GPL"
__copyright__ = "Copyright 2021, Michael Reda"
__status__ = "Beta"

# ---------------------------------
# Import Libraries
import sys
import site

sysPaths = []
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)
sitePackage_dir = r""
site.addsitedir(sitePackage_dir)


# ---------------------------------
# Variables


# ---------------------------------
# Start Here


# Main Function
def main():
    pass


if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
