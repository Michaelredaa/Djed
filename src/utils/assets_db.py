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
import site
from functools import wraps
from urllib.parse import unquote

sysPaths = [os.getenv("DJED_ROOT"), os.getenv("DJED_ROOT")+"/src"]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)


# ---------------------------------
# Variables

from utils.file_manager import FileManager

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


class Connect():
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
                name TEXT,
                creation_date DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                modification_date DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                uuid TEXT DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
                UNIQUE(name)
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
                    usd_geo_file TEXT,
                    abc_file TEXT,
                    fbx_file TEXT,
                    source_file TEXT,
                    substance_file TEXT,
                    mesh_data TEXT DEFAULT "{default_data}",
                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE
                    UNIQUE(asset_id)
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_map_type_table(self, conn):
        table_name = "map_type"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    type TEXT,
                    UNIQUE(name)
                    );
        '''
        cur.execute(query)

    @Connect.db
    def create_texture_table(self, conn):
        table_name = "textures"

        # self.delete_table(table_name=table_name)
        cur = conn.cursor()
        query = f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    map_id INTEGER NOT NULL,
                    udim_num INTEGER,
                    texture_path TEXT,
                    material_name TEXT,
                    res INTEGER,

                    FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE CASCADE,
                    FOREIGN KEY (map_id) REFERENCES map_type (id)
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

    def create_default_tables(self):
        self.create_asset_table()
        self.create_map_type_table()
        self.create_projects_table()
        self.create_tags_table()
        self.create_asset_tags_table()
        self.create_asset_projects_table()

        self.create_geometry_table()
        self.create_texture_table()
        self.create_thumbnail_table()

    @Connect.db
    def get_last_id(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT last_insert_rowid();")
        ids = cur.fetchall()
        return ids[0][0]

    @Connect.db
    def get_asset_id(self, conn, asset_name):
        cur = conn.cursor()
        cur.execute(f'SELECT id from assets WHERE name="{asset_name}"')
        ids = cur.fetchone()
        if ids:
            return ids[0]
        else:
            return 0

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
                ORDER BY modification_date DESC LIMIT 1
        '''
        cur.execute(query)
        data = cur.fetchall()
        if data:
            return data[0][0]

    @Connect.db
    def update_date(self, conn, asset_name):
        now = datetime.datetime.now()
        current_date = now.strftime("%Y/%m/%d, %H:%M:%S")
        cur = conn.cursor()
        query = f'''
                UPDATE assets 
                SET modification_date = "{current_date}"
                WHERE
                name = "{asset_name}"
        '''
        cur.execute(query)

    @Connect.db
    def update_texture_maps(self, conn):
        map_types = fm.get_cfg("texture_types_new")

        for map_type in map_types:
            cur = conn.cursor()
            query = f'''
                    INSERT INTO map_type
                    (name, type) 
                    VALUES
                    ("{map_type}", "{map_types.get(map_type, "")}")
                    ON CONFLICT(name) 
                    DO NOTHING
            '''

            cur.execute(query)

    @Connect.db
    def add_asset(self, conn, asset_name):
        now = datetime.datetime.now()
        current_date = now.strftime("%Y/%m/%d, %H:%M:%S")
        cur = conn.cursor()
        query = f'''
                INSERT INTO assets 
                (name, modification_date)
                VALUES
                ("{asset_name}", "{current_date}")
                ON CONFLICT(name) 
                DO UPDATE
                SET modification_date = "{current_date}";
        '''
        cur.execute(query)

    @Connect.db
    def add_geometry(self, conn, asset_name, **kwargs):

        '''obj_file="", usd_geo_file="", abc_file="", fbx_file="", source_file="", substance_file="", mesh_data=""'''
        self.update_date(asset_name=asset_name)
        for col in kwargs:
            cur = conn.cursor()
            query = f'''
                    INSERT INTO geometry 
                    (asset_id, {col})
                    VALUES
                    ((SELECT id from assets WHERE name='{asset_name}'), '{kwargs.get(col)}')
                    ON CONFLICT(asset_id) 
                    DO UPDATE
                    SET {col} = '{kwargs.get(col)}';

            '''
            cur.execute(query)

    @Connect.db
    def get_geometry(self, conn, asset_name, **kwargs):

        cols = ", ".join(kwargs.keys())
        cur = conn.cursor()
        query = f'''
                SELECT {cols} FROM geometry 
                WHERE
                asset_id = (SELECT id from assets WHERE name="{asset_name}")
        '''
        cur.execute(query)
        data = cur.fetchall()[0]
        return dict(zip(kwargs.keys(), data))

    @Connect.db
    def add_tag(self, conn, asset_name, tag_name):
        cur = conn.cursor()
        tag_id = cur.execute(f'SELECT id FROM tags WHERE name="{tag_name}";').fetchone()
        if tag_id:
            tag_id = tag_id[0]
        else:
            cur.execute(f'INSERT INTO tags (name) VALUES ("{tag_name}");')
            tag_id = cur.lastrowid

        cur.execute(f'''SELECT asset_id, tag_id FROM asset_tags
                        WHERE 
                        asset_id = (SELECT id FROM assets WHERE name = "{asset_name}")
                        AND
                        tag_id = {tag_id}''')

        if not cur.fetchall():
            query = f'''
                    INSERT INTO asset_tags (asset_id, tag_id) 
                    VALUES 
                    ((SELECT id from assets WHERE name="{asset_name}"), {tag_id});
            '''
            cur.execute(query)

    @Connect.db
    def add_project(self, conn, asset_name, project_name):
        cur = conn.cursor()
        project_id = cur.execute(f'SELECT id FROM projects WHERE name="{project_name}";').fetchone()
        if project_id:
            project_id = project_id[0]
        else:
            cur.execute(f'INSERT INTO projects (name) VALUES ("{project_name}");')
            project_id = cur.lastrowid

        cur.execute(f'''SELECT asset_id, project_id FROM asset_projects
                        WHERE 
                        asset_id = (SELECT id FROM assets WHERE name = "{asset_name}")
                        AND
                        project_id = {project_id}''')

        if not cur.fetchall():
            query = f'''
                    INSERT INTO asset_projects (asset_id, project_id) 
                    VALUES 
                    ((SELECT id from assets WHERE name="{asset_name}"), {project_id});
            '''
            cur.execute(query)

    @Connect.db
    def add_textures(self, conn, asset_name, map_type_name, texture_path, udim_num, material_name="", resolution=""):
        cur = conn.cursor()
        result = cur.execute(f'''SELECT texture_path FROM textures
                            WHERE
                            asset_id = (SELECT id from assets WHERE name="{asset_name}")
                            AND 
                            map_id = (SELECT id from map_type WHERE name="{map_type_name}")
                            AND
                            material_name = "{material_name}"
                            ''')

        old_tex_path = result.fetchone()

        if not old_tex_path:
            query = f'''
                    INSERT INTO textures (asset_id, map_id, texture_path, udim_num, material_name, res)
                    VALUES
                    (
                    (SELECT id from assets WHERE name="{asset_name}"),
                    (SELECT id from map_type WHERE name="{map_type_name}"),
                    "{texture_path}",
                    {udim_num},
                    "{material_name}",
                    "{resolution}")
                    ;
            '''
        else:
            query = f'''
                    UPDATE textures
                    SET
                    texture_path = "{texture_path}",
                    udim_num = {udim_num},
                    res = "{resolution}"
                    WHERE
                    asset_id = (SELECT id from assets WHERE name="{asset_name}")
                    AND
                    map_id = (SELECT id from map_type WHERE name="{map_type_name}")
                    AND
                    material_name = "{material_name}"
                    ;
            '''

        cur.execute(query)

    @Connect.db
    def get_textures(self, conn, uuid):

        materials = {}

        cur = conn.cursor()

        query = f'''
                        SELECT material_name FROM 
                        assets 
                        LEFT JOIN textures ON assets.id=textures.asset_id
                        WHERE
                        assets.uuid = '{uuid}'
                        GROUP BY textures.material_name
                '''
        cur.execute(query)

        for material_name in cur.fetchall():
            if not material_name:
                continue
            material_name = material_name[0]
            materials[material_name] = {}
            query = f'''
                            SELECT textures.texture_path, textures.udim_num, textures.res, map_type.name, map_type.type  FROM 
                            textures 
                            LEFT JOIN map_type ON textures.map_id=map_type.id
                            WHERE
                            textures.material_name = '{material_name}'
                    '''
            cur.execute(query)
            textures = cur.fetchall()
            for row in textures:
                texture_path, udim_num, res, name, type = row
                materials[material_name][name] = {}
                materials[material_name][name]["type"] = type
                materials[material_name][name]["texture_path"] = texture_path
                materials[material_name][name]["udim_num"] = udim_num
                materials[material_name][name]["res"] = res

        return materials

    @Connect.db
    def get_assets_data(self, conn):

        cur = conn.cursor()
        query = f'''
                SELECT * FROM 
                assets 
                LEFT JOIN geometry ON assets.id=geometry.asset_id

        '''
        cur.execute(query)
        data = cur.fetchall()

        return data

    @Connect.db
    def get_asset(self, conn, uuid):

        asset = {}
        asset_name = self.get_asset_name(uuid=uuid)
        geometries = self.get_geometry(asset_name=asset_name, obj_file='', usd_geo_file='', abc_file='', fbx_file='')
        materials = self.get_textures(uuid=uuid)

        asset["name"] = asset_name
        asset["geos"] = geometries
        asset["mtls"] = materials

        return asset

    @Connect.db
    def get_tags(self, conn, asset_name):

        cur = conn.cursor()
        query = f'''
                SELECT name FROM tags
                WHERE
                id IN (
                    SELECT tag_id FROM 
                    asset_tags 
                    WHERE 
                    asset_id = (SELECT id from assets WHERE name="{asset_name}")
                )

        '''
        cur.execute(query)
        tags = cur.fetchall()

        return [x[0] for x in tags if x[0]]

    @Connect.db
    def get_projects(self, conn, asset_name):

        cur = conn.cursor()
        query = f'''
                SELECT name FROM projects
                WHERE
                id IN (
                    SELECT project_id FROM 
                    asset_projects 
                    WHERE 
                    asset_id = (SELECT id from assets WHERE name="{asset_name}")
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

    def delete_asset_projects(self, asset_name=None, asset_id=None):
        if asset_id is None:
            asset_id = self.get_asset_id(asset_name=asset_name)
        self.delete_row(table_name="project_tags", col="asset_id", value=asset_id)

    def delete_asset_tags(self, asset_name=None, asset_id=None):
        if asset_id is None:
            asset_id = self.get_asset_id(asset_name=asset_name)
        self.delete_row(table_name="asset_tags", col="asset_id", value=asset_id)

    @Connect.db
    def set_thumbnail(self, conn, asset_name=None, asset_id=None, thumb_path=""):
        if asset_id is None:
            asset_id = self.get_asset_id(asset_name=asset_name)

        if thumb_path == "":
            return
        else:
            thumb_path = unquote(thumb_path)

        cur = conn.cursor()
        query = f'''
                INSERT INTO thumbnail  
                (asset_id, thumb_path)
                VALUES
                ("{asset_id}", "{thumb_path}") 

        '''
        cur.execute(query)
        data = cur.fetchall()

        return data

    @Connect.db
    def get_thumbnail(self, conn, asset_name, latest=True):

        asset_id = self.get_asset_id(asset_name=asset_name)
        cur = conn.cursor()
        query = f'''
                SELECT thumb_path FROM 
                assets 
                LEFT JOIN thumbnail ON assets.id=thumbnail.asset_id
                WHERE assets.id={asset_id}

        '''
        cur.execute(query)
        data = cur.fetchall()
        if latest:
            return data[-1][0]
        else:
            return [x[0] for x in data]


# Main Function
def main():
    db = AssetsDB()
    # db.create_default_tables()
    # db.create_geometry_table()
    data = json.dumps({'foo': 'bar'})
    db.add_geometry(asset_name="tv_table", mesh_data=f'{data}')
    # x = db.add_tag(asset_name="ABAGORA", tag_name="tag1")
    # x = db.get_assets_data()
    # print(db.get_tags(asset_name="ABAGORA"))

    # print(db.get_thumbnail(asset_name="tv_table"))
    # print(db.add_textures(asset_name="tv_table", map_type_name="_", texture_path="bar", udim_num=10, material_name="", resolution=""))
    # db.get_asset(uuid='a990d365-62f4-43ff-81bf-63422dc5cefb')


if __name__ == '__main__':
    
    main()
    

