# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# import libraries
import subprocess
import sys
import os
import re
import json
from pathlib import Path

DJED_ROOT = os.getenv('DJED_ROOT')
utils_path = os.path.join(DJED_ROOT, 'src')

sysPaths = [DJED_ROOT, utils_path]

for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

from utils.decorators import error
from utils.dialogs import message


# ---------------------------------

class FileManager():
    def __init__(self):
        self.root = os.getenv("DJED_ROOT")

    def resolve_path(self, source_path, **kwargs):
        """
        To resolve the given paths like relative path and $project
        :param source_path: the unresolved path
        :param kwargs: args to resolve with
        :return: resolved path
        """

        relatives_to = kwargs.get('relatives_to', '')

        resolved_path = Path(relatives_to)

        if source_path.count("../") > 0:
            resolved_path = resolved_path.parents[source_path.count("../") - 1]
            resolved_path = resolved_path.joinpath(source_path.rsplit("../", 1)[-1])

        variables = kwargs.get('variables', {})
        for var in variables:
            resolved_path = str(resolved_path).replace(var, variables.get(var))

        return resolved_path

    @error(name=__name__)
    def get_ssp_settings(self):
        """
        Substance painter Dialog export settings
        :return:
        """

        settings_path = os.path.join(self.root, "Scripts", "dcc", "Substance", "plugins", "substance_settings.json")
        if not os.path.isfile(settings_path):
            message(None, "Error", "Can not get substance settings file.")
            return

        return self.read_json(settings_path)

    def get_spp_export_presets(self):
        export_preset = os.path.join(self.user_documents, "spp_export_prsets.json")
        if os.path.isfile(export_preset):
            return self.read_json(export_preset)

    def set_spp_export_presets(self, data):
        export_preset = os.path.join(self.user_documents, "spp_export_prsets.json")
        self.write_json(export_preset, data)

    @error(name=__name__)
    def get_cfg(self, key):
        """
        To get the value from configuration with given key
        :param key: (str) the key name
        :return: type as the configuration
        """

        cfg_path = os.path.join(self.root, "cfg.json")
        if not os.path.isfile(cfg_path):
            print("Can not get the configuration file")
            return
        data = self.read_json(cfg_path)
        return data[key]

    @error(name=__name__)
    def read_json(self, json_path):
        """
        To read json file
        :param json_path: the system path of json
        :return: (dict)
        """
        with open(json_path, 'r') as f:
            return json.load(f)

    @error(name=__name__)
    def write_json(self, json_path, data):
        with open(json_path, 'w') as f:
            return json.dump(data, f, indent=4)

    @property
    @error(name=__name__)
    def user_documents(self):
        user_dir = Path.home().joinpath('Documents', 'Djed')
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    @property
    @error(name=__name__)
    def user_db(self):
        return self.user_documents.joinpath('assets.db')

    @error(name=__name__)
    def set_user_json(self, **kwargs):
        # json_path = os.path.join(self.user_documents(), "Djed.json").replace("\\", "/")
        json_path = self.user_documents.joinpath("Djed.json")

        if json_path.is_file():
            data = self.read_json(json_path)
        else:
            data = {}
        for key in kwargs:
            data[key] = kwargs[key]

        self.write_json(json_path, data)

    @error(name=__name__)
    def get_user_json(self, key, key1=None):
        # json_path = os.path.join(self.user_documents(), "Djed.json").replace("\\", "/")
        json_path = self.user_documents.joinpath("Djed.json")

        data = {}

        if not json_path.is_file():
            self.user_documents.mkdir(parents=True, exist_ok=True)
            self.write_json(json_path, data)

        user_data = self.read_json(json_path)
        if key in user_data:
            global_data = self.get_cfg(key)
            if not key1:
                return user_data.get(key)

            nested_data = user_data[key]
            if key1 in nested_data:
                return nested_data[key1]
            else:
                # get from global
                value = global_data.get(key1)
                nested_data[key1] = value
                self.set_user_json(**{key: nested_data})
                return value
        else:
            value = self.get_cfg(key)
            self.set_user_json(**{key: value})
            return value

    @error(name=__name__)
    def list_dirs(self, directory):
        return [x for x in os.listdir(directory) if os.path.isdir(os.path.join(directory, x))]

    @error(name=__name__)
    def list_files(self, directory, ext=".*"):
        return [x for x in os.listdir(directory) if
                os.path.isfile(os.path.join(directory, x)) and re.search(ext + "$", x)]

    @error(name=__name__)
    def list_images(self, directory):
        img_extensions = self.get_cfg("texture_extensions")

        return [x for x in os.listdir(directory) if
                (os.path.isfile(os.path.join(directory, x))) and ((x.split('.')[-1] in img_extensions))]

    @error(name=__name__)
    def ck_udim(self, texture_name):
        if re.search(r"[.-_]\d+\.", texture_name):
            return True

    @error(name=__name__)
    def get_sgName_from_textures(self, directory):
        # to extract the sg name form list of images
        sgs = []
        for img in self.list_images(directory):
            items = re.findall(r"_[a-zA-Z0-9]*", img)
            sg = items[-2][1:]
            if len(sg) <= 3:
                try:
                    sg = items[-3][1:] + "_" + items[-2][1:]
                except:
                    pass

            sgs.append(sg)
        return list(set(sgs))

    @error(name=__name__)
    def ck_tex(self, texture_name):
        texture_types = self.get_cfg("texture_types")

        for _type in texture_types:
            if not isinstance(texture_types[_type], list):
                continue
            for regex in texture_types[_type]:
                if re.search(regex, texture_name):
                    return _type

    @error(name=__name__)
    def make_dirs(self, path, *args):
        if not os.path.isdir(os.path.join(path, *args)):
            os.makedirs(os.path.join(path, *args))

        return os.path.join(path, *args).replace("\\", "/")

    @error(name=__name__)
    def get_latest_version(self, path, prefix='v', padding=4, ret_path=False):

        self.make_dirs(path)
        all_versions = os.listdir(path)
        if len(all_versions) < 1:
            version = prefix + "1".zfill(padding)
        else:
            all_versions = [x for x in all_versions if re.search(prefix + r"\d+", x)]
            if len(all_versions) <= 1:
                version = prefix + "1".zfill(padding)
            else:
                all_versions_ints = [int(re.findall(r"\d+", x)[0]) for x in all_versions]
                version = prefix + str(max(all_versions_ints)).zfill(padding)

        if ret_path:
            return os.path.join(path, version).replace("\\", "/")
        else:
            return version

    def get_latest_file_version(self, root, ext='.*', prefix='v', padding=4, ret_path=False):
        root = Path(root)

        files = root.glob(f'*{ext}')
        names = [x.name for x in files if re.search(prefix + "\d+", x.name)]
        if len(names) < 1:
            return 0

        all_versions_ints = [int(re.findall(r"\d+", x)[0]) for x in names]
        max_version_num = max(all_versions_ints)
        latest_version = prefix + str(max_version_num).zfill(padding)

        file_name = re.sub(prefix + r'\d+', latest_version, names[0])
        if ret_path:
            return root.joinpath(file_name).as_posix(), max_version_num
        else:
            return file_name, max_version_num

    @error(name=__name__)
    def version_up(self, path, prefix='v', padding=4):
        self.make_dirs(path)
        increment = "1".zfill(padding)
        up_version = "{}{}".format(prefix, increment)
        all_versions = os.listdir(path)
        if len(all_versions) < 1:
            ret_path = os.path.join(path, up_version)
        else:
            latest_version = self.get_latest_version(path, prefix=prefix, padding=padding, ret_path=False)

            num_str = re.findall(r"\d+", latest_version)
            if not num_str:
                ret_path = os.path.join(path, up_version)
            else:
                increment = str(int(num_str[0]) + 1).zfill(padding)
                up_version = "{}{}".format(prefix, increment)
                ret_path = os.path.join(path, up_version)
        return ret_path.replace("\\", "/"), up_version

    @error(name=__name__)
    def version_file_up(self, file_path, prefix='v', padding=4):

        file_path = Path(str(file_path))
        ext = file_path.suffix
        file_dir = file_path.parent
        file_dir.mkdir(parents=True, exist_ok=True)

        files = file_dir.glob(f'*{ext}')

        names = [x.name for x in files if re.search(prefix + r'\d+', x.name)]
        if len(names) < 1:
            file_name = re.sub(prefix+r'\d+', prefix+'0001', file_path.name)
            return file_dir.joinpath(file_name).as_posix()

        latest_file, num = self.get_latest_file_version(file_dir, ext=ext, prefix=prefix,padding=padding, ret_path=True)
        increment_file = re.sub(
            prefix + str(num).zfill(padding),
            prefix + str(num+1).zfill(padding),
            latest_file
        )

        return increment_file

    def open_in_expoler(self, path):
        path = Path(str(path))

        if path.is_file():
            subprocess.Popen(f'explorer /select,"{path}"')

        elif path.is_dir():
            subprocess.Popen(f'explorer "{path}"')

    def dict_depth(self, dictionary):
        if isinstance(dictionary, dict):
            return 1 + (max(map(self.dict_depth, dictionary.values())) if dictionary else 0)
        return 0



# Main function
def main():
    pass
    fm = FileManager()
    fm.version_file_up(
        r"D:\3D\working\projects\Generic\03_Workflow\Assets\tv_table\Scenefiles\sur\substance\tv_table")
    # print(fm.resolve_path('../../foo', relatives_to='c:/users/michael'))


if __name__ == '__main__':
    main()
