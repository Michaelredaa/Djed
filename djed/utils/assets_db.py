# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import datetime
import json
import sqlite3
import sys
import os
import traceback
from functools import wraps
from urllib.parse import unquote

sysPaths = [os.getenv("DJED_ROOT")]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from djed.settings.settings import get_textures_patterns
from djed.utils.file_manager import FileManager

# ---------------------------------
# Variables

fm = FileManager()


def connect(db_file):
    def connect_(query_func):
        @wraps(query_func)
        def connect_wrapper(*args, **kwargs):
            try:
                conn = sqlite3.connect(db_file)
                query_func(conn, *args, **kwargs)
            except Exception as e:
                raise e
            else:
                conn.commit()
                conn.close()

        return connect_wrapper

    return connect_


class Connect(object):
    db_file = None

    def __init__(self, db_file=None):
        if db_file is None:
            db_file = fm.user_db
        Connect.db_file = db_file

    def db(query_func):
        @wraps(query_func)
        def connect_wrapper(*args, **kwargs):
            try:
                conn = sqlite3.connect(Connect.db_file)
                cur = conn.cursor()
                ret_data = query_func(*args, conn, **kwargs)
            except Exception as e:
                print(traceback.format_exc())
                raise e
            else:
                conn.commit()
                conn.close()
                return ret_data

        return connect_wrapper

    def set_db_file(self, db_file):
        Connect.db_file = db_file

    def get_db_file(self):
        return Connect.db_file

    db = staticmethod(db)


class AssetsDB(Connect):

    def __init__(self, db_file=None):
        super(AssetsDB, self).__init__(db_file)

        if db_file:
            if not os.path.isdir(os.path.dirname(db_file)):
                os.makedirs(os.path.dirname(db_file))

            Connect.db_file = db_file
        self.create_default_tables()

    @Connect.db
    def delete_table(self, conn, table_name):
        cur = conn.cursor()

        query = f'''DROP TABLE IF EXISTS {table_name}'''
        cur.execute(query)

    @Connect.db
    def delete_row(self, conn, table_name, col, value):
        cur = conn.cursor()

        query = f'''DELETE from {table_name} where {col} = {value}'''
        cur.execute(query)

    @Connect.db
    def create_asset_table(self, conn):
        table_name = "assets"
        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gallery INTEGER DEFAULT 0,
                uuid TEXT DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
                UNIQUE(uuid)
                );
        '''
        cur.execute(query)

    @Connect.db
    def create_geometry_table(self, conn):
        table_name = "geometry"

        # self.delete_table(table_name=table_name)
        default_data = {}
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    obj_file TEXT,
                    abc_file TEXT,
                    data JSON DEFAULT "{{}}",
                    version INTEGER NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_usd_table(self, conn):
        table_name = "usd"

        # self.delete_table(table_name=table_name)
        default_data = {}
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    usd_file TEXT,
                    geo_file TEXT,
                    mtl_file TEXT,
                    data JSON DEFAULT "{{}}",
                    version INTEGER NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_material_table(self, conn):
        table_name = "material"

        # self.delete_table(table_name=table_name)
        default_data = {}
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    data JSON DEFAULT "{{}}",
                    version INTEGER NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_workingfile_table(self, conn):
        table_name = "workingfile"

        # self.delete_table(table_name=table_name)
        default_data = {}
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT,
                    extension TEXT,
                    dcc TEXT,
                    data JSON DEFAULT "{{}}",
                    version INTEGER NOT NULL
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_asset_workingfile_table(self, conn):
        table_name = "asset_workingfile"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER,
                    workingfile_id INTEGER,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    FOREIGN KEY (workingfile_id) REFERENCES workingfile (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_thumbnail_table(self, conn):
        table_name = "thumbnail"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    thumb_path TEXT,
                    thumbnail BLOB,
                    version INTEGER NOT NULL,
                    data JSON DEFAULT "{{}}",
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_projects_table(self, conn):
        table_name = "projects"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_tags_table(self, conn):
        table_name = "tags"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_asset_tags_table(self, conn):
        table_name = "asset_tags"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER,
                    tag_id INTEGER,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_asset_projects_table(self, conn):
        table_name = "asset_projects"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER,
                    project_id INTEGER,
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_asset_metadata_table(self, conn):
        table_name = "metadata"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER,
                    
                    creation_date DATETIME DEFAULT (strftime('%Y/%m/%d %H:%M:%S', 'now', 'localtime')),
                    modification_date DATETIME DEFAULT (strftime('%Y/%m/%d %H:%M:%S', 'now', 'localtime')),
                    
                    data JSON DEFAULT "{{}}",
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    );
        '''
        cur.execute(query)

    def create_default_tables(self):
        self.create_asset_table()
        self.create_projects_table()
        self.create_tags_table()
        self.create_asset_tags_table()
        self.create_asset_projects_table()

        self.create_geometry_table()
        self.create_usd_table()
        self.create_material_table()
        self.create_workingfile_table()
        self.create_asset_workingfile_table()
        self.create_workingfile_table()

        self.create_thumbnail_table()

        self.create_asset_metadata_table()

    @Connect.db
    def add_asset(self, conn, asset_name, gallery=0, **kwargs):
        cur = conn.cursor()

        # add asset
        query = f'''
                        INSERT INTO assets 
                        (name, gallery)
                        VALUES
                        ("{asset_name}", {gallery});
                '''
        cur.execute(query)
        conn.commit()

        # UUID
        cur = conn.cursor()
        cur.execute(f'SELECT uuid FROM assets ORDER BY id DESC LIMIT 1')
        uuid_str = cur.fetchone()[0]

        # add asset data
        query = f'''
                        INSERT INTO metadata 
                        (asset_id, data)
                        VALUES
                        ((SELECT id from assets WHERE uuid='{uuid_str}'), '{json.dumps(kwargs)}');
                '''
        cur.execute(query)

        return uuid_str

    @Connect.db
    def get_last_id(self, conn):
        cur = conn.cursor()
        cur.execute(f'SELECT id FROM assets ORDER BY id DESC LIMIT 1')
        ids = cur.fetchall()
        return ids[0][0]

    @Connect.db
    def get_last_uuid(self, conn):
        cur = conn.cursor()
        cur.execute(f'SELECT uuid FROM assets ORDER BY id DESC LIMIT 1')
        uuids = cur.fetchall()
        return uuids[0][0]

    @Connect.db
    def get_asset_id(self, conn, asset_name):
        cur = conn.cursor()
        cur.execute(f'SELECT id from assets WHERE name="{asset_name}"')
        ids = cur.fetchall()
        if ids:
            return [x[0] for x in ids]
        else:
            return []

    @Connect.db
    def get_asset_uuid(self, conn, asset_name):
        cur = conn.cursor()
        cur.execute(f'SELECT uuid from assets WHERE name="{asset_name}"')
        uuids = cur.fetchall()
        if uuids:
            return [x[0] for x in uuids]
        else:
            raise Exception(f"Asset '{asset_name}' not found")

    @Connect.db
    def get_id_from_uuid(self, conn, uuid):
        cur = conn.cursor()
        cur.execute(f'SELECT id from assets WHERE uuid="{uuid}"')
        ids = cur.fetchone()
        return ids[0]

    @Connect.db
    def get_asset_name(self, conn, uuid):
        cur = conn.cursor()
        cur.execute(f'SELECT name from assets WHERE uuid="{uuid}"')
        names = cur.fetchone()
        if names:
            return names[0]
        else:
            return ""

    @Connect.db
    def get_latest_edit_asset_name(self, conn):
        cur = conn.cursor()

        query = f'''
                SELECT name FROM assets 
                LEFT JOIN metadata ON assets.id=metadata.asset_id
                ORDER BY modification_date DESC LIMIT 1
        '''
        cur.execute(query)
        data = cur.fetchall()
        if data:
            return data[0][0]

    @Connect.db
    def update_date(self, conn, uuid):
        now = datetime.datetime.now()
        current_date = now.strftime("%Y/%m/%d, %H:%M:%S")
        cur = conn.cursor()
        query = f'''
                UPDATE metadata
                SET modification_date = "{current_date}"
                WHERE
                asset_id = (SELECT id FROM assets WHERE uuid="{uuid}")
        '''
        cur.execute(query)

    @Connect.db
    def get_versions(self, conn, uuid, table_name):
        """TO get all data of table and sort them descending according to version number"""
        cur = conn.cursor()

        cur.row_factory = sqlite3.Row

        query = f'''
                SELECT * FROM {table_name}
                WHERE
                asset_id = (SELECT id FROM assets WHERE uuid="{uuid}")
                ORDER BY version DESC
        '''
        cur.execute(query)
        data = [dict(i) for i in cur.fetchall()]

        # convert data to dict
        for item in data:
            item["data"] = json.loads(item["data"])

        return data

    @Connect.db
    def get_versions_tables(self, conn, uuid, table_name):
        """TO get all data of table from 2 separates tables
        and sort them descending according to version number"""
        cur = conn.cursor()

        cur.row_factory = sqlite3.Row

        query = f'''
                SELECT * FROM asset_{table_name}
                LEFT JOIN assets ON asset_{table_name}.asset_id=assets.id
                LEFT JOIN {table_name} ON asset_{table_name}.{table_name}_id={table_name}.id
                
                WHERE 
                uuid="{uuid}"
                ORDER BY version DESC
        '''

        cur.execute(query)
        data = [dict(i) for i in cur.fetchall()]

        # convert data to dict
        for item in data:
            item["data"] = json.loads(item["data"])

        return data

    @Connect.db
    def update_texture_maps(self, conn):
        map_types = get_textures_patterns()

        for map_type in map_types:
            cur = conn.cursor()
            if 'color' in map_type:
                _type = 'color'
            else:
                _type = 'float'

            query = f'''
                    INSERT INTO map_type
                    (name, type) 
                    VALUES
                    ("{map_type}", "{_type}")
                    ON CONFLICT(name) 
                    DO NOTHING
            '''

            cur.execute(query)

    @Connect.db
    def add_geometry(self, conn, uuid, obj_file="", abc_file="", **kwargs):

        """obj_file="", abc_file="" """
        self.update_date(uuid=uuid)

        all_versions = self.get_versions(uuid=uuid, table_name="geometry")

        if all_versions:
            version = all_versions[0]["version"] + 1
        else:
            version = 1

        cur = conn.cursor()
        query = f'''
                INSERT INTO geometry 
                (asset_id, obj_file, abc_file, version, data)
                VALUES
                (
                    (SELECT id FROM assets WHERE uuid='{uuid}'),
                    '{obj_file}',
                    '{abc_file}',
                    {version},
                    '{json.dumps(kwargs)}'
                );

        '''

        cur.execute(query)

    @Connect.db
    def add_usd(self, conn, uuid, usd_file="", geo_file="", mtl_file="", **kwargs):

        self.update_date(uuid=uuid)

        all_versions = self.get_versions(uuid=uuid, table_name="usd")

        if all_versions:
            version = all_versions[0]["version"] + 1
        else:
            version = 1

        cur = conn.cursor()
        query = f'''
                INSERT INTO usd 
                (asset_id, usd_file, geo_file, mtl_file, version, data)
                VALUES
                (
                    (SELECT id FROM assets WHERE uuid='{uuid}'),
                    '{usd_file}',
                    '{geo_file}',
                    '{mtl_file}',
                    {version},
                    '{json.dumps(kwargs)}'
                );

        '''

        cur.execute(query)

    @Connect.db
    def add_material(self, conn, uuid, **kwargs):

        self.update_date(uuid=uuid)

        all_versions = self.get_versions(uuid=uuid, table_name="material")

        if all_versions:
            version = all_versions[0]["version"] + 1
        else:
            version = 1

        cur = conn.cursor()
        query = f'''
                INSERT INTO usd 
                (asset_id, version, data)
                VALUES
                (
                    (SELECT id FROM assets WHERE uuid='{uuid}'),
                    {version},
                    '{json.dumps(kwargs)}'
                );

        '''

        cur.execute(query)

    def dcc_workfile_version(self, all_versions, dcc='maya'):
        if all_versions:
            for v in all_versions:
                if v['dcc'] == dcc:
                    version = v["version"] + 1
                    break
            else:
                version = 1
        else:
            version = 1

        return version

    @Connect.db
    def add_workingfile(self, conn, uuid, filepath="", extension="", dcc="", **kwargs):

        self.update_date(uuid=uuid)

        all_versions = self.get_versions_tables(uuid=uuid, table_name="workingfile")

        version = self.dcc_workfile_version(all_versions, dcc)

        cur = conn.cursor()
        query = f'''
                INSERT INTO workingfile 
                (filepath, extension, dcc, version, data)
                VALUES
                (
                    '{filepath}',
                    '{extension}',
                    '{dcc}',
                    {version},
                    '{json.dumps(kwargs)}'
                );

        '''

        cur.execute(query)
        workfile_id = cur.lastrowid
        conn.commit()

        cur = conn.cursor()
        query = f'''
                INSERT INTO asset_workingfile 
                (asset_id, workingfile_id)
                VALUES
                (
                    (SELECT id FROM assets WHERE uuid='{uuid}'),
                    '{workfile_id}'
                );

        '''
        cur.execute(query)

    @Connect.db
    def add_tag(self, conn, uuid, tag_name):
        cur = conn.cursor()

        tag_id = cur.execute(f'SELECT id FROM tags WHERE name="{tag_name}";').fetchone()
        if tag_id:
            tag_id = tag_id[0]
        else:
            cur.execute(f'INSERT INTO tags (name) VALUES ("{tag_name}");')
            tag_id = cur.lastrowid

        cur.execute(f'''SELECT asset_id, tag_id FROM asset_tags
                        WHERE 
                        asset_id = (SELECT id FROM assets WHERE uuid = "{uuid}")
                        AND
                        tag_id = {tag_id}''')

        if not cur.fetchall():
            query = f'''
                    INSERT INTO asset_tags (asset_id, tag_id) 
                    VALUES 
                    ((SELECT id from assets WHERE uuid="{uuid}"), {tag_id});
            '''
            cur.execute(query)

    @Connect.db
    def add_project(self, conn, uuid, project_name):
        cur = conn.cursor()
        project_id = cur.execute(f'SELECT id FROM projects WHERE name="{project_name}";').fetchone()
        if project_id:
            project_id = project_id[0]
        else:
            cur.execute(f'INSERT INTO projects (name) VALUES ("{project_name}");')
            project_id = cur.lastrowid

        cur.execute(f'''SELECT asset_id, project_id FROM asset_projects
                        WHERE 
                        asset_id = (SELECT id FROM assets WHERE uuid = "{uuid}")
                        AND
                        project_id = {project_id}''')

        if not cur.fetchall():
            query = f'''
                    INSERT INTO asset_projects (asset_id, project_id) 
                    VALUES 
                    ((SELECT id from assets WHERE uuid="{uuid}"), {project_id});
            '''
            cur.execute(query)

    @Connect.db
    def get_assets_data(self, conn):

        cur = conn.cursor()

        query = f'''
                SELECT uuid FROM assets
                WHERE
                gallery=1
        '''
        cur.execute(query)
        uuids = cur.fetchall()

        data = []
        for uuid in uuids:
            data.append(self.get_asset(uuid[0]))

        return data

    def get_asset(self, uuid):

        asset = {}
        asset_name = self.get_asset_name(uuid=uuid)
        geometry = self.get_versions(uuid=uuid, table_name='geometry')
        usd = self.get_versions(uuid=uuid, table_name='usd')
        material = self.get_versions(uuid=uuid, table_name='material')
        workingfile = self.get_versions_tables(uuid=uuid, table_name='workingfile')

        asset["name"] = asset_name
        asset["geometry"] = geometry
        asset["usd"] = usd
        asset["material"] = material
        asset["workingfile"] = workingfile

        return asset

    @Connect.db
    def get_tags(self, conn, uuid):

        cur = conn.cursor()
        query = f'''
                SELECT name FROM tags
                WHERE
                id IN (
                    SELECT tag_id FROM 
                    asset_tags 
                    WHERE 
                    asset_id = (SELECT id from assets WHERE uuid="{uuid}")
                )

        '''
        cur.execute(query)
        tags = cur.fetchall()

        return [x[0] for x in tags if x[0]]

    @Connect.db
    def get_projects(self, conn, uuid):

        cur = conn.cursor()
        query = f'''
                SELECT name FROM projects
                WHERE
                id IN (
                    SELECT project_id FROM 
                    asset_projects 
                    WHERE 
                    asset_id = (SELECT id from assets WHERE uuid="{uuid}")
                )

        '''
        cur.execute(query)
        projects = cur.fetchall()

        return [x[0] for x in projects if x[0]]

    @Connect.db
    def all_tags(self, conn):

        cur = conn.cursor()
        query = f'''
                SELECT name FROM tags
                ORDER BY 
                name
        '''
        cur.execute(query)
        tags = cur.fetchall()

        return [x[0] for x in tags if x[0]]

    @Connect.db
    def all_projects(self, conn):

        cur = conn.cursor()
        query = f'''
                SELECT name FROM projects
                ORDER BY 
                name
        '''
        cur.execute(query)
        projects = cur.fetchall()

        return [x[0] for x in projects if x[0]]

    def delete_asset_projects(self, uuid):
        self.delete_row(
            table_name="asset_projects",
            col="asset_id",
            value=self.get_id_from_uuid(uuid=uuid)
        )

    def delete_asset_tags(self, uuid):
        self.delete_row(
            table_name="asset_tags",
            col="asset_id",
            value=self.get_id_from_uuid(uuid=uuid)
        )

    @Connect.db
    def add_thumbnail(self, conn, uuid, thumb_path="", **kwargs):

        if thumb_path == "":
            return
        else:
            thumb_path = unquote(thumb_path)

        all_versions = self.get_versions(uuid=uuid, table_name="thumbnail")

        if all_versions:
            version = all_versions[0]["version"] + 1
        else:
            version = 1

        cur = conn.cursor()
        query = f'''
                INSERT INTO thumbnail  
                (asset_id, thumb_path, version, data)
                VALUES
                ("{self.get_id_from_uuid(uuid=uuid)}", "{thumb_path}", {version}, '{json.dumps(kwargs)}') 

        '''
        cur.execute(query)
        data = cur.fetchall()

        return data

    @Connect.db
    def get_metadata(self, conn, _id):
        cur = conn.cursor()
        query = f'''
                SELECT data FROM 
                json_data 
                WHERE id=1

        '''
        cur.execute(query)
        data = cur.fetchall()
        return data[0][0]


# Main Function
def main():
    db = AssetsDB()


if __name__ == '__main__':
    main()
