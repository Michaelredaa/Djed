import os
import sys
import site
from pathlib import Path



DJED_ROOT = Path(os.getenv("DJED_ROOT"))
sysPaths = [DJED_ROOT.as_posix()]
for sysPath in sysPaths:
    if sysPath not in sys.path:
        sys.path.append(sysPath)

import pyblish.api
from djed.settings.settings import get_asset_root, get_dcc_cfg
from djed.dcc.maya.api.cmds import Maya


ma = Maya()
class CollectAssetData(pyblish.api.InstancePlugin):
    """Collect asset data"""

    order = pyblish.api.CollectorOrder + 0.2
    label = 'Collect Asset Data'
    families = ["asset"]

    def process(self, instance):

        selection = instance.data['selection']

        instance.data['assets_key'] = {
            "asset_root": get_asset_root(asset_name=instance.name),
            "asset_name": instance.name
        }

        instance.data['unit'] = ma.get_unit()

