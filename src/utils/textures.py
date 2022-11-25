# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys
import re
import ast
from pathlib import Path

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'src')

sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from settings.settings import get_textures_settings, get_textures_patterns


def list_textures(directory):
    img_extensions = get_textures_settings('extensions')

    return [x for x in os.listdir(directory) if
            (os.path.isfile(os.path.join(directory, x))) and ((x.split('.')[-1].lower() in img_extensions))]


def ck_udim(texture_name):
    if re.search(r"[.-_]\d+\.", texture_name):
        return True


def get_sgName_from_textures(directory):
    # to extract the sg name form list of images
    sgs = []
    for img in list_textures(directory):
        img = img.split(' ')[0]
        items = re.findall(r"_[a-zA-Z0-9]*", img)
        for item in items:
            if re.search(r'(i?)sg', item):
                sgs.append(item[1:])
                continue
        try:
            sg = items[-2][1:]
            if len(sg) >= 4:
                try:
                    sg = items[-4][1:] + "_" + items[-3][1:]
                except:
                    pass

            sgs.append(sg)
        except:
            pass
    return list(set(sgs))


def texture_type_from_name(texture_name):
    texture_types = get_textures_patterns()

    # reversed to take the color before weight e.g. specular_color before specular
    for _type in reversed(list(texture_types.keys())):
        str_to_list = texture_types[_type]
        if not isinstance(str_to_list, list):
            continue
        for regex in str_to_list:
            if re.search(regex, texture_name):
                return _type


if __name__ == '__main__':
    path = r"path/foo/bar/baseColor"
    print(texture_type_from_name(path))
    print(__name__)
