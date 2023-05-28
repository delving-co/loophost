__version__ = '0.2.9'

import getpass
import os
import pathlib
import platform
import sys


LOOPHOST_DOMAIN = "loophost.dev"
TUNNEL_DOMAIN = "fling.team"

PYEX = sys.executable
HUBDIR = os.path.dirname(os.path.realpath(__file__))

def GET_LOOPHOST_DIR():
    DIR = pathlib.Path("\\", "Users", "Shared", ".loophost")
    if platform.system().lower().startswith('win'):
        DIR = pathlib.Path("\\Users", "Public", ".loophost")
    os.makedirs(DIR, exist_ok=True)
    os.chdir(DIR)
    return os.path.abspath(os.path.curdir)


_USERNAME = None
def GET_FLINGUSER_NAME():
    global _USERNAME
    if _USERNAME is None:
        flinguser_path = pathlib.Path(GET_LOOPHOST_DIR(), "flinguser.txt")
        if os.path.exists(flinguser_path):
            with open(flinguser_path, "r") as userfile:
                _USERNAME = userfile.read()
    return _USERNAME


def DATA_FILE_PATH():
    return pathlib.Path(GET_LOOPHOST_DIR(), "loophost.json")
