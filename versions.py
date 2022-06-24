import discord
import youtube_dl
import os
import sys

def test_versions():
    to_test = [(discord,"2.0.0b4","py-cord"), (youtube_dl,"2021.12.17","youtube-dl"),]
    updated = []
    for module, target_ver, pkg_name in to_test:
        current_ver = get_version(module)
        print(module.__name__, "at", current_ver)
        if current_ver != target_ver:
            os.system(f"pip install {pkg_name}=={target_ver}")
            updated.append(f"{module.__name__}=={target_ver}")

    if updated:
        print(f"Had to update packages {updated}, please rerun to use updated versions")
        sys.exit(0)

def get_version(module):
    try:
        return module.__version__
    except Exception:
        return module.version.__version__