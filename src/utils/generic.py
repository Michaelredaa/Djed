# -*- coding: utf-8 -*-
"""
Documentation:
"""
import time

from utils.file_manager import FileManager

fm = FileManager()

def wait_until(somepredicate, timeout, period=0.25, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if somepredicate(**kwargs):
            return True
        time.sleep(period)
    return False


def merge_dicts(dict1, dict2):
    """
    https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries

    TO merge two dictionary together and dict2 over dict1
    :return: generator of dictionary
    """

    # at python 3.9:: dict1 | dict2

    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield k, dict(merge_dicts(dict1[k], dict2[k]))
            else:
                # If one of teh values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first, and we move on.
                yield k, dict2[k]
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield k, dict1[k]
        else:
            yield k, dict2[k]


def material_conversion(from_host, from_renderer, to_host, to_renderer):

    cfg = fm.get_cfg('renderer')
    plugs = cfg.get('plugs')
    nodes = cfg.get('nodes')

    if (from_host == 'standard') or (from_renderer == 'standard'):
        plugs_dict = {
            plug_name: plugs[plug_name].get(to_host).get(to_renderer)
            for plug_name in plugs
        }
        nodes_dict = {
            node_name: nodes[node_name].get(to_host).get(to_renderer)
            for node_name in nodes
        }

    else:
        plugs_dict = {
            plugs[plug_name].get(from_host).get(from_renderer).get('name'):
                plugs[plug_name].get(to_host).get(to_renderer)
            for plug_name in plugs
        }
        nodes_dict = {
            nodes[node_name].get(from_host).get(from_renderer).get('name'):
                nodes[node_name].get(to_host).get(to_renderer)
            for node_name in nodes
        }

    return {"plugs": plugs_dict, "nodes": nodes_dict}


if __name__ == '__main__':
    dict1 = {1: {"a": "A"}, 2: {"b": "B"}}
    dict2 = {2: {"b": "C"}, 3: {"d": "D"}}

    print(dict(merge_dicts(dict1, dict2)))
    print(dict1 | dict2)
