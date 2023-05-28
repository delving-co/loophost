import getpass
import json
import os
import platform
import sys
import pathlib
import subprocess
from subprocess import run
import webbrowser
from certbot.main import main as certmain
from fling_cli.auth import gh_authenticate

from loophost.launchd_plist import register_tunnel
from loophost import (
    LOOPHOST_DOMAIN,
    TUNNEL_DOMAIN,
    HUBDIR,
    GET_LOOPHOST_DIR,
    GET_FLINGUSER_NAME,
    DATA_FILE_PATH,
)


def post_install_one():
    print("Installing LoopHost...")
    localuser_file = pathlib.Path(GET_LOOPHOST_DIR(), "localuser.txt")
    with open(localuser_file, "w+") as userfile:
        userfile.write(getpass.getuser())
    authenticate_with_fling()
    if not platform.system().lower().startswith('win'):
        issue_certs()
    create_update_loophost_json()
    register_tunnel(
        "flinghub",
        pathlib.Path(HUBDIR, "plist", "loophost.plist.template"),
        pathlib.Path(
            pathlib.Path.home(), "Library/LaunchAgents/dev.fling.hub.local.plist"
        ),
    )

    step_two_as_root()


def post_install_two():
    if platform.system().lower().startswith('win'):
        issue_certs()
    setup_launchd_scripts()


def authenticate_with_fling():
    if not GET_FLINGUSER_NAME():
        gh_authenticate()
    if not GET_FLINGUSER_NAME():
        raise Exception("Github authentication failed, can't continue install.")



def issue_certs():
    USERNAME = GET_FLINGUSER_NAME()
    print("Generating SSL certificates (this may take a minute)...")
    cmd = [
            "certonly",
            "--config-dir", "./",
            "--work-dir", "./",
            "--logs-dir", "./",
            "--non-interactive",
            "--expand",
            "--agree-tos",
            f"-m webmaster@{LOOPHOST_DOMAIN}",
            "--authenticator=fling_authenticator",
            f'-d *.{USERNAME}.{LOOPHOST_DOMAIN}',
            f'-d *.{USERNAME}.{TUNNEL_DOMAIN}',
            f'-d {USERNAME}.{LOOPHOST_DOMAIN}',
            "--fling_authenticator-propagation-seconds=15",
        ]
    
    certmain(cmd)


def create_update_loophost_json():
    USERNAME = GET_FLINGUSER_NAME()
    data = None
    if os.path.exists(DATA_FILE_PATH()):
        with open(DATA_FILE_PATH(), "r") as datafile:
            data = json.loads(datafile.read())
    else:
        data = {"apps": {}, "share": {}}
    data.update(
        {
            "fqdn": f"{USERNAME}.{LOOPHOST_DOMAIN}",
            "tunnel": f"{USERNAME}.{TUNNEL_DOMAIN}",
        }
    )
    with open(DATA_FILE_PATH(), "w") as datafile:
        datafile.write(json.dumps(data))
    return data


def setup_launchd_scripts():
    register_tunnel(
        "flinghub",
        pathlib.Path(HUBDIR, "plist", "hub.plist.template"),
        "/Library/LaunchDaemons/dev.fling.hub.plist",
    )
    print("All done.")


def step_two_as_root():
    print(
        """Switching to root/admin user to install web services on ports 443 and 80\n\r
        (you will be prompted for your password)"""
    )
    cmd = "sudo python3 -m loophost.step_two"
    if platform.system().lower().startswith('win'):
        cmd = "python3 -m loophost.step_two"
    run(
        cmd,
        shell=True,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        # stdin=subprocess.PIPE,
        cwd=GET_LOOPHOST_DIR(),
        check=True
    )
    print("All finished.")
    webbrowser.open(f"https://{GET_FLINGUSER_NAME()}.{LOOPHOST_DOMAIN}")
    sys.exit()

