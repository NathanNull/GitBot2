import os
import sys
import shutil
from types import ModuleType

def test_versions():
    import discord
    import yt_dlp
    to_test = [(discord,"2.4.0","py-cord"), (yt_dlp,"2023.02.17","yt-dlp"),]
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

def get_version(module:ModuleType):
    try:
        return module.__version__
    except Exception:
        return module.version.__version__

def place_ffmpeg():
    os.environ['PATH'] += os.pathsep + os.path.dirname(__file__)
    print(f"{shutil.which('ffmpeg.exe')} exists")
    
def ready():
    test_versions()
    place_ffmpeg()