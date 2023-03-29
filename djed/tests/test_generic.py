# -*- coding: utf-8 -*-
"""
Documentation: 
"""


# ---------------------------------
# Import Libraries
import sys
import os

import unittest

DJED_ROOT = os.getenv('DJED_ROOT')
sysPaths = [DJED_ROOT]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.utils import generic

# ---------------------------------
# Variables


# ---------------------------------
# Start Here
class TestGeneric(unittest.TestCase):
    def test_validate_name(self):
        names = {
            'foo.bar': 'foo_bar',
            'foo bar': 'foo_bar',
            'foo?bar': 'foo_bar',
            'foo_bar ': 'foo_bar',

        }
        for name in names:
            self.assertEqual(names[name], generic.validate_name(name))

    def test_merge_dicts(self):
        dict1 = {1: {"a": "A"}, 2: {"b": "B"}}
        dict2 = {2: {"b": "C"}, 3: {"d": "D"}}

        self.assertEqual(
            dict(generic.merge_dicts(dict1, dict2)),
            {1: {'a': 'A'}, 2: {'b': 'C'}, 3: {'d': 'D'}}
        )


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
