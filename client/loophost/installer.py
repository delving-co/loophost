import json
import os
import platform
from pathlib import Path
from subprocess import run
import webbrowser
from certbot.main import main as certmain
from fling_cli.auth import gh_authenticate
from loophost.utils_mac import register_launchd_service
from loophost import (
    LOOPHOST_DOMAIN,
    TUNNEL_DOMAIN,
    HUBDIR,
    GET_LOOPHOST_DIR,
    GET_FLINGUSER_NAME,
    DATA_FILE_PATH,
)


def step_one_mac():
    issue_certs()
    register_launchd_service(
        "flinghub",
        Path(HUBDIR, "plist", "loophost.plist.template"),
        Path(Path.home(), "Library/LaunchAgents/dev.fling.hub.local.plist"),
    )
    register_launchd_service(
        "loophosttunnel",
        Path(HUBDIR, "plist", "tunnel.plist.template"),
        Path(Path.home(), "Library/LaunchAgents/dev.fling.hub.tunnel.plist"),
    )


def step_two_mac():
    register_launchd_service(
        "flinghub",
        Path(HUBDIR, "plist", "hub.plist.template"),
        "/Library/LaunchDaemons/dev.fling.hub.plist",
    )


def step_one_win():
    pass


def step_two_win():
    issue_certs()
    _setup_win_services()


def step_one_linux():
    pass


def step_two_linux():
    pass


def _setup_win_services():
    # build steps for the win_hub and win_lp binaries
    # Make sure the win_hub binary and win_lp binary are convenient
    # copy them to the pywin32 site packages folder
    # run them with install start-auto parameters
    # run them with start parameters
    pass


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
        "--config-dir",
        "./",
        "--work-dir",
        "./",
        "--logs-dir",
        "./",
        "--non-interactive",
        "--expand",
        "--agree-tos",
        f"-m webmaster@{LOOPHOST_DOMAIN}",
        "--authenticator=fling_authenticator",
        f"-d *.{USERNAME}.{LOOPHOST_DOMAIN}",
        f"-d *.{USERNAME}.{TUNNEL_DOMAIN}",
        f"-d {USERNAME}.{LOOPHOST_DOMAIN}",
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


def step_two_as_root():
    print(
        """Switching to root/admin user to install web services on ports 443 and 80\n\r
        (you will be prompted for your password)"""
    )
    cmd = "python3 -m loophost.postinstall_two"
    if not platform.system().lower().startswith('win'):
        cmd = "sudo " + cmd
    run(cmd, shell=True, cwd=GET_LOOPHOST_DIR(), check=True)


def open_loophost():
    webbrowser.open(f"https://{GET_FLINGUSER_NAME()}.{LOOPHOST_DOMAIN}")
