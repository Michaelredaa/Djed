# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os

DJED_ROOT = os.getenv("DJED_ROOT")


def get_stylesheet():
    return open(f"{DJED_ROOT}/djed/utils/resources/stylesheet.qss").read()


if __name__ == '__main__':
    print(__name__)
