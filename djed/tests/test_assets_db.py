# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import sys
import os
import re

import unittest

DJED_ROOT = os.getenv('DJED_ROOT')
sysPaths = [DJED_ROOT]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.utils.assets_db import AssetsDB, Connect
from djed.utils.file_manager import FileManager

# ---------------------------------
# Variables

fm = FileManager()
db = AssetsDB(fm.user_documents.joinpath("tests/database/djed.db"))


# ---------------------------------
# Start Here
class TestDataBase(unittest.TestCase):

    @Connect.db
    def test_create_default_tables(self, conn):
        table_names = [
            "assets",
            "asset_projects",
            "asset_tags",
            "asset_workingfile",
            "geometry",
            "metadata",
            "projects",
            "tags",
            "thumbnail",
            "usd",
            "workingfile",
        ]

        for table_name in table_names:
            cur = conn.cursor()
            cur.execute(f'SELECT name FROM sqlite_master WHERE name="{table_name}"')
            tables = cur.fetchall()
            self.assertTrue(tables)

    def test_add_asset(self):
        # add asset
        asset_uuid = db.add_asset(asset_name="asset_a", key="value")

        # assert UUID
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
        self.assertTrue(
            re.match(
                uuid_pattern,
                str(asset_uuid)
            ),
            asset_uuid
        )

        # asset asset name
        self.assertEqual(
            db.get_asset_name(uuid=asset_uuid),
            "asset_a"
        )

        # asset id
        asset_ids = db.get_asset_id(asset_name="asset_a")
        latest_id = db.get_last_id()
        self.assertTrue(
            latest_id in asset_ids,
            f"Latest id `{latest_id}` not the same of the last added asset `{asset_ids}`"
        )

    def test_add_geometry(self):
        asset_uuid = db.get_last_uuid()

        # add data
        db.add_geometry(
            uuid=asset_uuid,
            obj_file='path/to/obj',
            abc_file='path/to/abc',
            key="value"
        )

        data = db.get_versions(uuid=asset_uuid, table_name='geometry')[0]

        self.assertEqual(data.get('obj_file'), 'path/to/obj')
        self.assertEqual(data.get('abc_file'), 'path/to/abc')
        self.assertIsInstance(data.get('data'), dict)

    def test_add_usd(self):
        asset_uuid = db.get_last_uuid()

        # add data
        db.add_usd(
            uuid=asset_uuid,
            usd_file='path/to/usd_file',
            geo_file='path/to/geo_file',
            key="value"
        )

        data = db.get_versions(uuid=asset_uuid, table_name='usd')[0]

        self.assertEqual(data.get('usd_file'), 'path/to/usd_file')
        self.assertEqual(data.get('geo_file'), 'path/to/geo_file')
        self.assertIsInstance(data.get('data'), dict)

    def test_add_workingfile(self):
        asset_uuid = db.get_last_uuid()

        # add data
        db.add_workingfile(
            uuid=asset_uuid,
            filepath='path/to/workingfile',
            extension='ma',
            dcc='maya',
            key="value"
        )

        data = db.get_versions_tables(uuid=asset_uuid, table_name='workingfile')[0]
        self.assertEqual(data.get('filepath'), 'path/to/workingfile')
        self.assertEqual(data.get('extension'), 'ma')
        self.assertEqual(data.get('dcc'), 'maya')
        self.assertIsInstance(data.get('data'), dict)

    def test_get_assets_data(self):
        # add data
        data = db.get_assets_data()
        self.assertIsInstance(data, list, f"{data}")
        for item in data:
            self.assertIsInstance(item, dict, f"{item}")

    def test_add_thumbnail(self):
        asset_uuid = db.get_last_uuid()

        # add data
        db.add_thumbnail(
            uuid=asset_uuid,
            thumb_path='path/to/thumb_path1',
        )

        data1 = db.get_versions(uuid=asset_uuid, table_name='thumbnail')[0]

        self.assertEqual(data1.get('thumb_path'), 'path/to/thumb_path1')
        self.assertIsInstance(data1.get('data'), dict, f"{data1}")

        # versioning
        db.add_thumbnail(
            uuid=asset_uuid,
            thumb_path='path/to/thumb_path2',
        )
        data2 = db.get_versions(uuid=asset_uuid, table_name='thumbnail')[0]

        self.assertTrue(data2['version'] > data1['version'], f"{data2['version']} > {data1['version']}")

    def test_add_tag(self):
        asset_uuid = db.get_last_uuid()
        db.add_tag(uuid=asset_uuid, tag_name='tag1')

        self.assertTrue('tag1' in db.get_tags(uuid=asset_uuid))

        db.delete_asset_tags(uuid=asset_uuid)
        self.assertFalse('tag1' in db.get_tags(uuid=asset_uuid))

    def test_add_project(self):
        asset_uuid = db.get_last_uuid()
        db.add_project(uuid=asset_uuid, project_name='project1')

        self.assertTrue('project1' in db.get_projects(uuid=asset_uuid))

        db.delete_asset_projects(uuid=asset_uuid)
        self.assertFalse('project1' in db.get_projects(uuid=asset_uuid))


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
