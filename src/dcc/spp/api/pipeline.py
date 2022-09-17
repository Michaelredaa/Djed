# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os
import sys

DJED_ROOT = os.getenv("DJED_ROOT")
scripts_path = os.path.join(DJED_ROOT, "src")

sysPaths = [DJED_ROOT, scripts_path]
for sysPath in sysPaths:
    if not sysPath in sys.path:
        sys.path.append(sysPath)



import substance_painter as sp

# ---------------------------------


Settings = {
    "OpenGL": sp.project.NormalMapFormat.OpenGL,
    "DirectX": sp.project.NormalMapFormat.DirectX,
    # ProjectWorkflow
    "Default": sp.project.ProjectWorkflow.Default,
    "TextureSetPerUVTile": sp.project.ProjectWorkflow.TextureSetPerUVTile,  # legacy
    "UVTile": sp.project.ProjectWorkflow.UVTile,  # Set per material containing multiple UV
    # Tangent space
    "PerVertex": sp.project.TangentSpace.PerVertex,
    "PerFragment": sp.project.TangentSpace.PerFragment,
    "default_texture_resolution": 1024

}

default_project = {
    "import_cameras": False,
    "default_texture_resolution": 1024,
    "normal_map_format": Settings["DirectX"],
    "project_workflow": Settings["UVTile"],
    "tangent_space_mode": Settings["PerVertex"]

}


def create_project(mesh_file: str, project_path=None, cfg=None):
    """
    To remotely create a new project
    :param mesh_file: (str) the mesh file path
    :param project_path: (str) the new project path
    :param cfg: (dict) the configuration of starting file
    :return:
    """

    if not cfg:
        cfg = default_project
    else:
        cfg = {}
        cfg["import_cameras"] = cfg["import_cameras"]
        cfg["default_texture_resolution"] = cfg["default_texture_resolution"]
        cfg["normal_map_format"] = Settings[cfg["normal_map_format"]]
        cfg["project_workflow"] = Settings[cfg["project_workflow"]]
        cfg["tangent_space_mode"] = Settings[cfg["tangent_space_mode"]]

        # open project
        if sp.project.is_open():
            sp.project.close()
        sp.project.create(mesh_file_path=mesh_file, settings=sp.project.Settings(**cfg))
        if sp.project.is_open():
            print("The project was successfully created.")

        # save project
        if project_path:
            sp.project.save_as(project_path)
            if not sp.project.needs_saving():
                print("As expected, there is nothing to save since this was just done.")


if __name__ == '__main__':
    print(__name__)
