import pyblish.api

from dcc.maya.api.cmds import Maya

import maya.cmds as cmds


class ExtractModel(pyblish.api.InstancePlugin):
    """
    To export the selected object
    """

    order = pyblish.api.ExtractorOrder + 0.01

    optional = True
    label = "Export Model"
    hosts = ["maya"]
    families = ["model"]
    active = True

    def process(self, instance):
        self.log.info("Initialize exporting the model")
        ma = Maya()

        data = instance.data

        cmds.select(data.get('name'), r=1)
        export_meshs = ma.export_selection(
            asset_dir=data.get('path'),
            asset_name=data.get('name'),
            export_type=data.get('extensions', []),
            _message=False,
        )
