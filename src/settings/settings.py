# -*- coding: utf-8 -*-
"""
Documentation:
"""
import json
import os
import sys
from pathlib import Path

from PySide2.QtWidgets import QApplication

DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, f"{DJED_ROOT}/src"]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.assets_db import AssetsDB
from utils.file_manager import FileManager
from utils.dialogs import message

fm = FileManager()

user_settings_dir = fm.user_documents.joinpath('settings')
user_settings_file = user_settings_dir.joinpath('settings.json')
root_settings_dir = Path(f"{DJED_ROOT}/src/settings/cfg")
root_settings_file = root_settings_dir.joinpath('settings.json')


def get_settings_data():
    if user_settings_file.is_file():
        try:
            data = fm.read_json(user_settings_file)
        except:
            data = []
            pass
    else:
        data = fm.read_json(root_settings_file)

    return data.get('items', [])


def set_settings_data(data_list):
    data = {'items': data_list}
    fm.write_json(user_settings_file, data)


def error_on_reading(key, dict_name):
    message(None, 'Error', f'Corrupted settings file.\nCan not get "{key}" from "{dict_name}" dict settings')


def get_dict(base_list, key):
    dict_list = [x for x in base_list if x.get('name') == key]
    if not dict_list:
        return False
    else:
        return dict_list[0]


def get_value(key, *args):
    items_list = get_settings_data()

    my_dict = {}
    for arg in args:
        my_dict = get_dict(items_list, arg)

        if not my_dict:
            error_on_reading(key, arg)
            return {}

        items_list = my_dict.get('children', [])
        for i, item in enumerate(items_list):
            if isinstance(item, str) and '$' in item:
                file_name = item.split('$')[-1] + '.json'
                file_path = user_settings_dir.joinpath(file_name)
                if not file_path.is_file():

                    file_path = root_settings_dir.joinpath(file_name)

                    if not file_path.is_file():
                        continue

                data = fm.read_json(file_path)
                items_list.pop(i)
                items_list.insert(i, data)

        items_list = my_dict.get('children', [])

    return my_dict


def set_value(value, *args):
    items_list = get_settings_data()

    my_dict = {}
    items_list_copy = items_list
    for arg in args:
        my_dict = get_dict(items_list_copy, arg)

        items_list_copy = my_dict.get('children', [])

    if not my_dict:
        return
    my_dict['value'] = value
    set_settings_data(items_list)


def get_colorspace_settings(key='aces_color_hdr'):
    value_dict = get_value(key, 'general', 'textures', 'colorspace', key)
    return value_dict.get('value', '')


def get_textures_settings(key='extensions'):
    value_dict = get_value(key, 'general', 'textures', 'patterns', key)
    return list(value_dict.get('value', ''))


def get_textures_patterns():
    value_dict = get_value('patterns', 'general', 'textures', 'patterns')
    patterns = {x['name']: x['value'] for x in value_dict.get('children', [])}
    patterns.pop('extensions')
    patterns.pop('hdr_extension')
    return patterns


def get_dcc_cfg(*args):
    value_dict = get_value(args[-1], *args)
    if 'data' in value_dict:
        values = {x['name']: x.get('value') for x in value_dict.get('data', [])}
        return values
    elif 'children' in value_dict:
        values = {x['name']: x.get('value') for x in value_dict.get('children', [])}
        return values
    else:
        return value_dict.get('value', '')


def material_conversion(from_host, from_renderer, to_host, to_renderer, node='standard_surface'):
    from_plugs = get_dcc_cfg(from_host, 'renderers', from_renderer, node + '_plugs')
    to_plugs = get_dcc_cfg(to_host, 'renderers', to_renderer, node + '_plugs')

    plugs = {from_plugs[i]['name']: to_plugs[j] for i, j in zip(from_plugs, to_plugs)}

    return plugs


def get_shading_node(host, renderer):
    render_dict = get_value(renderer, host, 'renderers', renderer)
    shading_nodes = {x['name']: x['value'] for x in render_dict.get('children', []) if 'value' in x}
    return shading_nodes


def shading_nodes_conversion(from_host, from_renderer, to_host, to_renderer):
    from_nodes = get_shading_node(from_host, from_renderer)
    to_nodes = get_shading_node(to_host, to_renderer)
    nodes = {from_nodes[i]: to_nodes[j] for i, j in zip(from_nodes, to_nodes)}
    return nodes


if __name__ == '__main__':

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # print(get_dcc_cfg('maya', 'renderers', 'arnold'))
    # print(get_value('arnold', 'maya', 'renderers', 'arnold'))
    # print(get_dcc_cfg("substance_painter", "texture_export"))
    set_value('512', "maya", "plugins", "maya_substance_painter", "default_texture_resolution")
    sys.exit(app.exec_())

    print(__name__)
