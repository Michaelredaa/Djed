# -*- coding: utf-8 -*-
"""
Documentation:
"""


import substance_painter as sp

def info(msg):
    substance_painter.logging.log(substance_painter.logging.INFO, "Djed", msg)


def error_(msg):
    substance_painter.logging.log(substance_painter.logging.ERROR, "Djed", msg)




from utils.dialogs import info

INTEGRATION_PLUGIN = None


class JS:
    def __init__(self):
        pass

    def exe(self, cmd):
        try:
            result = sp.js.evaluate(cmd)
            return result
        except RuntimeError:
            info(f'Can not evaluate the "{cmd}" command')
            return

    def export_mesh(self, path=None):
        """
        TO export the current mesh
        :param path: the mesh path, if None it will export at the same path of original file
        :return:
        """

        if path is None:
            path = "alg.project.lastImportedMeshUrl()"
        else:
            path = f'"file:///{path}"'
        cmd = f'alg.project.exportMesh({path})'
        return self.exe(cmd)

    def open_export_window(self, **kwargs):
        """
        TO open the export window
        kwargs:
            format = "png",
            path = "/path/to/export",
            preset= "preset_name"
        :return:
        """
        cmd = f'alg.mapexport.showExportDialog({kwargs})'
        return self.exe(cmd)

    def get_current_export_preset(self):
        cmd = 'alg.mapexport.getProjectExportPreset()'
        return self.exe(cmd)

    def get_current_export_option(self):
        cmd = 'alg.mapexport.getProjectExportOptions()'
        return self.exe(cmd)

    def get_export_path(self):
        cmd = 'alg.mapexport.exportPath()'
        return self.exe(cmd)

    def get_documentStructure(self):
        cmd = f'alg.mapexport.documentStructure()'
        return self.exe(cmd)

    def export_texture(self, preset, path, extension, **kwargs):
        cmd = f'alg.mapexport.exportDocumentMaps("{preset}", "{path}", "{extension}")'
        return self.exe(cmd)



class SubstanceIntegration():
    def __init__(self):
        self.fm = FileManger()
        self.js = JS()

        self.menu = QtWidgets.QMenu("DJED")
        self.main_window = substance_painter.ui.get_main_window()

        self.asset_name = db.get_latest_edit_asset_name()
        self.project_dir = ""
        self.exported_textures = dict()

        self.startUp()


if __name__ == '__main__':
    print(__name__)
