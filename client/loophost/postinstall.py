import json
import os
import sys
import pathlib
import subprocess
from subprocess import run
from fling_cli.auth import gh_authenticate
from loophost.launchd_plist import register_tunnel
from loophost import (
    LOOPHOST_DOMAIN,
    TUNNEL_DOMAIN,
    TARGET_DIR,
    HUBDIR,
    USERNAME,
    DATA_FILE_PATH,
)


def post_install_one():
    print("Installing LoopHost...")
    os.makedirs(pathlib.Path(TARGET_DIR, "certs"), exist_ok=True)
    os.chdir(TARGET_DIR)
    with open("localuser.txt", "w+") as userfile:
        userfile.write(os.getlogin())
    authenticate_with_fling()
    issue_certs()
    create_update_loophost_json()
    register_tunnel(
        "flinghub",
        pathlib.Path(HUBDIR, "plist", "loophost.plist.template"),
        pathlib.Path(
            pathlib.Path.home(), "Library/LaunchAgents/dev.fling.hub.local.plist"
        ),
    )

    restart_as_sudo()


def post_install_two():
    setup_launchd_scripts()


def authenticate_with_fling():
    global USERNAME
    gh_authenticate()
    if not os.path.exists(pathlib.Path(TARGET_DIR, "flinguser.txt")):
        raise Exception("Github authentication failed, can't continue install.")
    with open(pathlib.Path(TARGET_DIR, "flinguser.txt"), "r") as userfile:
        USERNAME = userfile.read()


def issue_certs():
    global USERNAME, TARGET_DIR
    print("Generating SSL certificates (this may take a minute)...")
    cmd = " ".join(
        [
            "certbot",
            "certonly",
            "--config-dir ./",
            "--work-dir ./",
            "--logs-dir ./",
            "--non-interactive",
            "--expand",
            "--agree-tos",
            f"-m webmaster@{LOOPHOST_DOMAIN}",
            "--authenticator=fling_authenticator",
            f'-d "*.{USERNAME}.{LOOPHOST_DOMAIN}"',
            f'-d "{USERNAME}.{LOOPHOST_DOMAIN}"',
            # "--force-renewal",
            "--fling_authenticator-propagation-seconds=15",
        ]
    )
    print(cmd)
    run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        cwd=TARGET_DIR,
        shell=True,
        check=True,
    )


def create_update_loophost_json():
    data = None
    if os.path.exists(DATA_FILE_PATH):
        with open(DATA_FILE_PATH, "r") as datafile:
            data = json.loads(datafile.read())
    else:
        data = {"apps": {}, "share": {}}
    data.update(
        {
            "fqdn": f"{USERNAME}.{LOOPHOST_DOMAIN}",
            "tunnel": f"{USERNAME}.{TUNNEL_DOMAIN}",
        }
    )
    with open(DATA_FILE_PATH, "w") as datafile:
        datafile.write(json.dumps(data))
    return data


def setup_launchd_scripts():
    register_tunnel(
        "flinghub",
        pathlib.Path(HUBDIR, "plist", "hub.plist.template"),
        "/Library/LaunchDaemons/dev.fling.hub.plist",
    )
    print("All done.")


def restart_as_sudo():
    global USERNAME
    print(
        "Switching to root user to install web services (you will be prompted for your password)"
    )
    run(
        "sudo python3 -m loophost.postinstall",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        cwd=TARGET_DIR,
    )
    print("All finished.")
    run(f"""/usr/bin/open "https://{USERNAME}.{LOOPHOST_DOMAIN}" """, shell=True)
    sys.exit()


if __name__ == "__main__":
    # TODO: Make this impotent and reentrant safe
    if os.geteuid() == 0:
        post_install_two()
    else:
        post_install_one()
