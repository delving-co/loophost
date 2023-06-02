__version__ = "1.2.7"

import getpass
import os
import pathlib
import platform
import sys
from string import Template


LOOPHOST_DOMAIN = "loophost.dev"
TUNNEL_DOMAIN = "fling.team"

PYEX = sys.executable
HUBDIR = os.path.dirname(os.path.realpath(__file__))


def GET_LOOPHOST_DIR():
    DIR = pathlib.Path("/Users", "Shared", ".loophost")
    if platform.system().lower().startswith("win"):
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


def store_localuser() -> None:
    localuser_file = pathlib.Path(GET_LOOPHOST_DIR(), "localuser.txt")
    with open(localuser_file, "w+") as userfile:
        userfile.write(getpass.getuser())
    return


def choose_proxy_binary():
    system = platform.system().lower()
    if "darwin" in system:
        if "arm" in platform.processor():
            return "loopproxy-darwin-arm64"
        return "loopproxy-darwin-amd64"
    elif "win" in system:
        return "loopproxy.exe"
    if "arm" in platform.processor():
        return "loopproxy-linux-arm64"
    return "loopproxy-linux-amd64"


def fill_template(template_path, target_path, project=None):
    TARGET_DIR = GET_LOOPHOST_DIR()
    d = {
        "CWD": TARGET_DIR,
        "USERNAME": GET_FLINGUSER_NAME(),
        "PYEX": PYEX,
        "HUBDIR": HUBDIR,
        "LOOPHOST_DOMAIN": LOOPHOST_DOMAIN,
        "TUNNEL_DOMAIN": TUNNEL_DOMAIN,
        "LOCAL_USER": pathlib.Path("localuser.txt").read_text().strip(),
        "PROJECT": project,
        "BINARY": choose_proxy_binary(),
    }
    with open(template_path, "r") as f:
        src = Template(f.read())
        result = src.substitute(d)
        with open(target_path, "w+") as o:
            o.write(result)
