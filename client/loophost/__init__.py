__version__ = '0.2.9'

import os
import pathlib
import sys


LOOPHOST_DOMAIN = "loophost.dev"
TUNNEL_DOMAIN = "fling.team"

if os.geteuid() != 0:
    os.makedirs(pathlib.Path(pathlib.Path.home(), ".flingdev"), exist_ok=True)
    os.chdir(pathlib.Path(pathlib.Path.home(), ".flingdev"))

TARGET_DIR = pathlib.Path(os.path.abspath(os.path.curdir))
PYEX = sys.executable
HUBDIR = os.path.dirname(os.path.realpath(__file__))
USERNAME = None
if os.path.exists(pathlib.Path(TARGET_DIR, "flinguser.txt")):
    with open(pathlib.Path(TARGET_DIR, "flinguser.txt"), "r") as userfile:
        USERNAME = userfile.read()

DATA_FILE_PATH = pathlib.Path(TARGET_DIR, "loophost.json")
