# -*- coding: utf-8 -*-
"""
Documentation: 
"""

# ---------------------------------
# Import Libraries
import os
import bpy.utils.previews


# ---------------------------------
# Variables
DJED_ROOT = os.getenv('DJED_ROOT')

# ---------------------------------
# Start Here
def get_icon(name):
    icon_dict = bpy.utils.previews.new()
    root = f'{DJED_ROOT}/djed/utils/resources/icons'

    for icon_name in ["mtlTexture.png", "shading.png"]:
        _name = icon_name.rsplit('.', 1)[0]
        try:
            if _name not in icon_dict:
                icon_dict.load(_name, os.path.join(root, icon_name), 'IMAGE')
        except:
            pass

    return icon_dict[name].icon_id


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
