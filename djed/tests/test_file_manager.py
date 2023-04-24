# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import sys
import os
import platform

import unittest

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'djed')
sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.utils.file_manager import FileManager, PathResolver

# ---------------------------------
# Variables
fm = FileManager()


# ---------------------------------
# Start Here
class TestFileManager(unittest.TestCase):

    def test_user_documents(self):
        user_document_dir = fm.user_documents.as_posix()

        if platform.system() == 'Windows':
            self.assertEqual(
                user_document_dir,
                f"C:/Users/{os.environ['USERNAME']}/Documents/Djed"
            )

    def test_resolve_path(self):
        resolved_path = fm.resolve_path(
            '../path/to/$version/$asset_name',
            relatives_to='/root/dir/file.ext',
            variables={'$version': 'v10', '$asset_name': 'Foo'}
        )

        self.assertEqual(resolved_path, '/root/dir/path/to/v10/Foo')

    def test_user_json(self):
        fm.set_user_json(foo='bar')
        self.assertEqual(fm.get_user_json('foo'), 'bar')


class TestPathResolver(unittest.TestCase):

    def test_resolve_path(self):
        resolver = PathResolver(r"{foo}/to/{bar}/{name}.{ext}")

        resolved_path = resolver.format(foo="/foo_value", bar="path/to/bar", name="asset", ext="abc")

        self.assertEqual(resolved_path, "/foo_value/to/path/to/bar/asset.abc")


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
