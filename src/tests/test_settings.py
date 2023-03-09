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
utils_path = os.path.join(DJED_ROOT, 'src')
sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from settings import settings


# ---------------------------------
# Variables


# ---------------------------------
# Start Here
class TestSettings(unittest.TestCase):
    def test_get_set_value(self):
        # test default values

        # string values
        key = 'srgb'

        settings.set_value('sRGB_new', 'general', 'textures', 'colorspace', key)
        value = settings.get_value(key, 'general', 'textures', 'colorspace', key).get('value', '')
        self.assertEqual(value, 'sRGB_new')

        settings.set_value('sRGB', 'general', 'textures', 'colorspace', key)
        value = settings.get_value(key, 'general', 'textures', 'colorspace', key).get('value', '')

        self.assertIsInstance(value, str)
        self.assertEqual(value, 'sRGB')

        # list values
        key = 'extensions'
        settings.set_value(['foo', 'bar'], 'general', 'textures', 'patterns', key)
        value = settings.get_value(key, 'general', 'textures', 'patterns', key).get('value', '')

        self.assertIsInstance(value, list)
        self.assertEqual(value, ['foo', 'bar'])

        # integer values
        key = 'command_port'
        value = settings.get_value(key, 'maya', 'configuration', key).get('value', '')
        self.assertIsInstance(value, int)

        settings.set_value(1000, 'maya', 'configuration', key)
        value = settings.get_value(key, 'maya', 'configuration', key).get('value', '')
        self.assertIsInstance(value, int)
        self.assertEqual(value, 1000)

        # boolean value
        key = 'obj'
        value = settings.get_value(key, 'maya', 'plugins', 'export_geometry', key).get('value', '')
        self.assertIsInstance(value, bool)

    def test_reset_value(self):
        key = 'command_port'
        default_value = settings.get_value(key, 'maya', 'configuration', key).get('default_value', '')
        settings.reset_value(key, 'maya', 'configuration', key)
        value = settings.get_value(key, 'maya', 'configuration', key).get('value', '')

        self.assertEqual(default_value, value)

    def test_get_textures_patterns(self):
        textures_patterns = settings.get_textures_patterns()
        self.assertIsInstance(textures_patterns, dict)

        for key in textures_patterns:
            self.assertIsInstance(textures_patterns[key], list)

    def test_material_attrs_conversion(self):
        from_host = "maya"
        from_renderer = "arnold"
        to_host = "clarisse"
        to_renderer = "autodesk_standard_surface"

        conversion = settings.material_attrs_conversion(from_host, from_renderer, to_host, to_renderer)

        self.assertIsInstance(conversion, dict)
        self.assertEqual(conversion['baseColor']['name'], 'base_color')
        self.assertIsInstance(conversion['baseColor']['inbetween'], list)


if __name__ == '__main__':
    unittest.main()
    print(__name__)
