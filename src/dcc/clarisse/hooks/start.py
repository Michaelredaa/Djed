# -*- coding: utf-8 -*-
"""
Documentation:
"""
import os


def add_clarisse_shelf(env_path=None):
    try:
        if not env_path:
            env_path = os.path.join(os.environ["APPDATA"], "Isotropix", "Clarisse", "5.0", "clarisse.env")

        shelf_path = "$DJED_ROOT/src/dcc/clarisse/shelves/djed_shelf.cfg"
        text = []
        with open(env_path, "r") as fh:
            for line in fh:
                if "IX_SHELF_CONFIG_FILE" in line:
                    if shelf_path in line:
                        return "Done"
                    else:
                        text.append(line.strip() + ";" + shelf_path + "\n")
                else:
                    text.append(line)
        with open(env_path, "w") as fh2:
            fh2.writelines(text)
        return "Done"

    except Exception as e:
        return str(e)


if __name__ == '__main__':
    print(__name__)
