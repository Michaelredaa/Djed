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

from djed.dcc.maya.api.cmds import Maya
from djed.utils.file_manager import FileManager

import maya.standalone

maya.standalone.initialize()
import maya.cmds as cmds

# ---------------------------------
# Variables
ma = Maya()
fm = FileManager()

user_root = fm.user_documents.joinpath("tests/maya")
user_root.mkdir(parents=True, exist_ok=True)
user_root = user_root.as_posix()


# ---------------------------------
# Start Here
class TestMaya(unittest.TestCase):
    def test_export_import_geo(self):
        node_name = 'djed_name'
        cmds.polyCube(name=node_name)

        obj_file = f"{user_root}/geo_obj.obj"
        abc_file = f"{user_root}/geo_abc.abc"
        usd_file = f"{user_root}/geo_usd.usd"
        fbx_file = f"{user_root}/geo_fbx.fbx"

        # create material
        sg, mtl = ma.create_and_assign_material(n='djed_materialMTL', objects=[node_name])

        self.assertTrue(cmds.objExists('djed_materialMTL'), f"{mtl}")
        self.assertTrue(cmds.objExists('djed_materialSG'), f"{sg}")

        # add attrs
        ma.add_attr_to_shapes(objects=[node_name], attr_name="materialBinding")
        self.assertTrue(
            cmds.getAttr(f'|{node_name}|{node_name}Shape.materialBinding') == 'djed_materialSG'
        )

        # export
        ma.export_geo(node_name=node_name, geo_path=obj_file)
        ma.export_geo(node_name=node_name, geo_path=abc_file, attrs=['materialBinding'])
        ma.export_geo(node_name=node_name, geo_path=usd_file)
        ma.export_geo(node_name=node_name, geo_path=fbx_file)

        self.assertTrue(os.path.isfile(obj_file), "OBJ file not exported")
        self.assertTrue(os.path.isfile(abc_file), "ABC file not exported")
        self.assertTrue(os.path.isfile(usd_file), "USD file not exported")
        self.assertTrue(os.path.isfile(fbx_file), "FBX file not exported")

        # import obj
        cmds.delete(node_name)
        nodes = ma.import_geo(obj_file)
        self.assertIsInstance(nodes, list)
        self.assertTrue(f'|{node_name}|{node_name}Shape' in nodes, f"{nodes}")

        # import abc
        cmds.delete(node_name)
        nodes = ma.import_geo(abc_file)
        self.assertIsInstance(nodes, list)
        self.assertTrue(f'|{node_name}|{node_name}Shape' in nodes, f"{nodes}")
        self.assertTrue(
            'materialBinding' in cmds.listAttr(f'|{node_name}|{node_name}Shape'),
            'materialBinding not on mesh'
        )
        self.assertTrue(
            cmds.getAttr(f'|{node_name}|{node_name}Shape.materialBinding') == 'djed_materialSG'
        )

        # import fbx
        cmds.delete(node_name)
        nodes = ma.import_geo(fbx_file)
        self.assertIsInstance(nodes, list)
        self.assertTrue(f'|{node_name}|{node_name}Shape' in nodes, f"{nodes}")

    def test_get_dimensions(self):
        node_name = 'dimension_name'
        cmds.polyCube(name=node_name)

        dimensions = ma.get_dimensions(node_name)

        self.assertIsInstance(dimensions, tuple)
        self.assertTrue(all(x == 1.0 for x in dimensions))

    def test_get_unit(self):

        cmds.currentUnit(linear="cm")
        unit = ma.get_unit()

        self.assertIsInstance(unit, str)
        self.assertTrue(unit == 'cm')

    def test_get_polycount(self):

        cmds.polyCube(name='cube01')
        cmds.polyCube(name='cube02')

        grp = cmds.group(['cube01', 'cube02'], n='count_grp')

        counts = ma.get_polycount(grp)

        self.assertIsInstance(counts, dict)
        self.assertTrue(counts.get('face'), 12)
        self.assertTrue(counts.get('vertex'), 16)
        self.assertTrue(counts.get('shell'), 2)

        #
        self.assertTrue(ma.is_root_node(grp))
        self.assertTrue(ma.is_group(grp))
        self.assertFalse(ma.is_root_node('cube01'))
        self.assertFalse(ma.is_group('cube01'))

    def test_selection(self):
        obj_name = cmds.polyCube(name='selected_cube')[0]

        ma.select(obj_name)

        self.assertEqual(ma.selection(), [obj_name])

        with ma.maintained_selection():
            cmds.polyCube(name='selected_cube2')
            ma.select('selected_cube2')

        self.assertEqual(ma.selection(), [obj_name], 'maintain selection now working')





# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
