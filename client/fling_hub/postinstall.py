import json
import os
import sys
import fling_hub
import pathlib
import subprocess
from subprocess import run, call, Popen
from fling_cli.auth import gh_authenticate
import shutil
from string import Template


LOOPHOST_DOMAIN = "loophost.dev"
TARGET_DIR = pathlib.Path(pathlib.Path.home(), ".flingdev")
PYEX = sys.executable
HUBDIR = os.path.dirname(os.path.realpath(fling_hub.__file__))
USERNAME = None
if os.path.exists(pathlib.Path(TARGET_DIR, "flinguser.txt")):
    with open(pathlib.Path(TARGET_DIR, "flinguser.txt"), "r") as userfile:
        USERNAME = userfile.read()


def restart_as_sudo():
    global USERNAME
    print(
        "Switching to root user to install web services (you will be prompted for your password)"
    )
    run(
        "sudo python3 -m fling_hub.postinstall",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        cwd=TARGET_DIR,
    )
    print("All finished.")
    run(f"open 'https://{USERNAME}.{LOOPHOST_DOMAIN}'")
    sys.exit()


def post_install_one():
    print("Installing LoopHost...")
    os.makedirs(pathlib.Path(TARGET_DIR, "certs"), exist_ok=True)
    os.chdir(TARGET_DIR)
    authenticate_with_fling()
    issue_certs()
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
    run(
        " ".join(
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
                "--fling_authenticator-propagation-seconds=15",
            ]
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        cwd=TARGET_DIR,
        shell=True,
        check=True,
    )


def setup_launchd_scripts():
    global USERNAME, TARGET_DIR, HUBDIR, PYEX
    if not os.path.exists(pathlib.Path(TARGET_DIR, "loophost.json")):
        with open(pathlib.Path(TARGET_DIR, "loophost.json"), "w") as datafile:
            data = {"apps": {}, "fqdn": f"{USERNAME}.{LOOPHOST_DOMAIN}"}
            datafile.write(json.dumps(data))
    shutil.copy2(pathlib.Path(HUBDIR, "loophost.plist.template"), TARGET_DIR)
    shutil.copy2(pathlib.Path(HUBDIR, "hub.plist.template"), TARGET_DIR)

    d = {"CWD": TARGET_DIR, "USERNAME": USERNAME, "PYEX": PYEX, "HUBDIR": HUBDIR}

    templates = [
        (
            pathlib.Path(HUBDIR, "loophost.plist.template"),
            "/Library/LaunchDaemons/dev.fling.hub.local.plist",
        ),
        (
            pathlib.Path(HUBDIR, "hub.plist.template"),
            "/Library/LaunchDaemons/dev.fling.hub.plist",
        ),
    ]

    for infile, outfile in templates:
        with open(infile, "r") as f:
            src = Template(f.read())
            result = src.substitute(d)
            with open(outfile, "w") as o:
                o.write(result)

            run(["launchctl", "unload", outfile], cwd=TARGET_DIR, user="root")
            run(["launchctl", "load", outfile], cwd=TARGET_DIR, user="root")
    print("All done.")


if __name__ == "__main__":
    # TODO: Make this impotent and reentrant safe
    if os.geteuid() == 0:
        post_install_two()
    else:
        post_install_one()
