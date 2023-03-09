# -*- coding: utf-8 -*-
"""
Documentation:
"""
import json
import os
import sys
from pathlib import Path
import ast



DJED_ROOT = os.getenv("DJED_ROOT")
sysPaths = [DJED_ROOT, f"{DJED_ROOT}/src"]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.file_manager import FileManager

fm = FileManager()

user_settings_dir = fm.user_documents.joinpath('settings')
user_settings_file = user_settings_dir.joinpath('settings.json')
root_settings_dir = Path(f"{DJED_ROOT}/src/settings/cfg")
root_settings_file = root_settings_dir.joinpath('settings.json')


def get_settings_data():
    """
    To get the settings data, trying to get the user data if failed, then get the global settings
    :return: list(dicts)
    """
    if user_settings_file.is_file():
        try:
            data = fm.read_json(user_settings_file)
        except:
            data = fm.read_json(root_settings_file)
            pass
    else:
        data = fm.read_json(root_settings_file)

    return data.get('items', [])


def set_settings_data(data_list):
    """
    To write the new settings into user file
    :param data_list: list(dicts) contain all settings
    :return: None
    """
    data = {'items': data_list}
    fm.write_json(user_settings_file, data)


def error_on_reading(key, dict_name):
    # popup message with error
    # message(None, 'Error', f'Corrupted settings file.\nCan not get "{key}" from "{dict_name}" dict settings')
    raise Exception(f'Can not get settings of "{key}" from "{dict_name}"')


def get_dict(base_list, key):
    """
    To get the dictionary of specific key in list of dicts
    :param base_list: list(dicts) of settings
    :param key: (str) the key name
    :return: (dict) dict that contain key
    """
    dict_list = [x for x in base_list if x.get('name') == key]
    if not dict_list:
        return False
    else:
        return dict_list[0]


def get_value(key, *args):
    """
    To get the value of specific key with specific args path
    :param key:(str) the key name
    :param args: (list) the list of path to specific key
    :return: (dict) dictionary that contain given key
    """
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
    """
    To set the settings value of given path of settings
    :param value: the new value
    :param args: (list) the list of path to specific key
    :return: None
    """
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


def reset_value(key, *args):
    """
    To reset the value of specific key with specific args path
    :param key:(str) the key name
    :param args: (list) the list of path to specific key
    :return: None
    """
    my_dict = get_value(key, *args)
    set_value(my_dict.get('default_value'), *args)


def get_colorspace_settings(key='aces_color_hdr'):
    """
    To get the colorspace settings of textures
    :param key:(str) the key name
    :return: the value of given key
    """
    value_dict = get_value(key, 'general', 'textures', 'colorspace', key)
    return value_dict.get('value', '')


def get_textures_settings(key='extensions'):
    """
    To get the textures settings
    :param key:(str) the key name
    :return: (list) list values of given key
    """
    value_dict = get_value(key, 'general', 'textures', 'patterns', key)
    values = value_dict.get('value', '[]')

    if not isinstance(values, list):
        values = json.loads(values.replace('\'', '"'))

    return values


def get_textures_patterns():
    """
    To get the textures settings patterns
    :return: (dict) dict patterns of textures {'name': [regx, regx*, ..]}
    """
    value_dict = get_value('patterns', 'general', 'textures', 'patterns')
    patterns = {x['name']: x['value'] for x in value_dict.get('children', [])}
    patterns.pop('extensions')
    patterns.pop('hdr_extension')

    try:
        for i in patterns:
            if isinstance(patterns[i], list):
                continue
            patterns[i] = json.loads(patterns[i].replace('\'', '"'))
    except json.decoder.JSONDecodeError:
        raise Exception(f"Invalid input date for textures patterns: {patterns}")

    return patterns


def get_dcc_cfg(*args):
    """
    To get the dcc full configuration of given path of args
    :param args: (list) list of path to settings
    :return: {dict} if table or multi seetings
            {value} of single field
    """
    value_dict = get_value(args[-1], *args)
    if 'data' in value_dict:
        values = {x['name']: x.get('value') for x in value_dict.get('data', [])}
        return values
    elif 'children' in value_dict:
        values = {x['name']: x.get('value') for x in value_dict.get('children', [])}
        return values
    else:
        return value_dict.get('value', '')

def material_attrs_conversion(from_host, from_renderer, to_host, to_renderer, node='standard_surface'):
    """
    To get the conversion between 2 nodes attributes
    :param from_host: (str) the source host name
    :param from_renderer: (str) the source renderer name
    :param to_host: (str) the distinction host name
    :param to_renderer: (str) the distinction renderer name
    :param node: (str) the standard node name
    :return: (dict) of key of source and value dict of distinction
    """
    from_plugs = get_dcc_cfg(from_host, 'renderers', from_renderer, node + '_plugs')
    to_plugs = get_dcc_cfg(to_host, 'renderers', to_renderer, node + '_plugs')

    plugs = {from_plugs[i]['name']: to_plugs[j] for i, j in zip(from_plugs, to_plugs)}
    return plugs

def get_material_type_names(host):
    """
    To get the available materials names
    :param host: (str) the host name
    :param node: (str) the standard node name
    :return: (list(str)) of materials names
    """
    renderers = get_dcc_cfg(host, 'renderers')
    return list(renderers)

def get_material_attrs(host, renderer, node='standard_surface'):
    """
    To get the material attributes
    :param host: (str) the host name
    :param renderer: (str) the renderer name
    :param node: (str) the standard node name
    :return: (dict) of key of standard plug and the value of node plug
    """
    plugs_original = get_dcc_cfg(host, 'renderers', renderer, node + '_plugs')
    plugs = {k: plugs_original[k] for k in plugs_original}
    return plugs


def get_shading_nodes(host, renderer):
    """
    To get the defined nodes in settings
    :param host: (str) the host name
    :param renderer: (str) the renderer name
    :return: (dict) of key of standard node name and value node name
    """
    render_dict = get_value(renderer, host, 'renderers', renderer)
    shading_nodes = {x['name']: x['value'] for x in render_dict.get('children', []) if 'value' in x}
    return shading_nodes


def shading_nodes_conversion(from_host, from_renderer, to_host, to_renderer):
    """
    To get the conversion of nodes types
    :param from_host: (str) the source host name
    :param from_renderer: (str) the source renderer name
    :param to_host: (str) the distinction host name
    :param to_renderer: (str) the distinction renderer name
    :param node: (str) the standard node name
    :return: (dict) of node names between 2 renderer
    """
    from_nodes = get_shading_nodes(from_host, from_renderer)
    to_nodes = get_shading_nodes(to_host, to_renderer)
    nodes = {from_nodes[i]: to_nodes[j] for i, j in zip(from_nodes, to_nodes)}
    return nodes


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # print(get_value('plugins', 'maya', 'plugins'))
    # print(get_value('arnold', 'maya', 'renderers', 'arnold'))
    # print(get_dcc_cfg("substance_painter", "texture_export"))
    # set_value('512', "maya", "plugins", "maya_substance_painter", "default_texture_resolution")
    print(get_textures_patterns())
    sys.exit(app.exec_())

    print(__name__)
