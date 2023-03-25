# -*- coding: utf-8 -*-
"""
Documentation:
"""

# ---------------------------------
# Import Libraries
import sys
import os
import importlib

import substance_painter_plugins

# ---------------------------------
# Variables
PLUGIN = None


# ---------------------------------PLUGIN
# Start Here
def start_plugin():
    global PLUGIN

    DJED_ROOT = os.getenv("DJED_ROOT")

    module_path = os.path.join(DJED_ROOT, "djed/dcc/spp/hooks/plugins/Djed.py")
    module_spec = importlib.util.spec_from_file_location('Djed_SPP', module_path)

    PLUGIN = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(PLUGIN)
    # PLUGIN = importlib.import_module("Djed")

    # Start the Plugin if it wasn't already:
    if not substance_painter_plugins.is_plugin_started(PLUGIN):
        substance_painter_plugins.start_plugin(PLUGIN)

    substance_painter_plugins.update_sys_path()


def close_plugin():
    global PLUGIN
    substance_painter_plugins.close_all_plugins()
    del PLUGIN


# Main Function
def main():
    pass


if __name__ == '__main__':
    main()
