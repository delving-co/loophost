import os
from pathlib import Path
from subprocess import run
import subprocess
import sys
from loophost import GET_LOOPHOST_DIR


def uninstall_one():
    if not os.path.exists(Path(GET_LOOPHOST_DIR(), "localuser.txt")):
        print("Seems to have already been uninstalled")
        exit(0)
    LOCAL_USER = Path(GET_LOOPHOST_DIR(), "localuser.txt").read_text().strip()
    for service in Path("/Users", LOCAL_USER, "Library", "LaunchAgents").glob(
        "dev.fling.hub*"
    ):
        run(["launchctl", "unload", service], cwd=GET_LOOPHOST_DIR())
        os.unlink(service)
    os.chdir(Path("/Users", LOCAL_USER))
    restart_as_sudo()


def uninstall_two():
    for service in Path("/Library", "LaunchDaemons").glob("dev.fling.hub*"):
        run(["launchctl", "unload", service], cwd=GET_LOOPHOST_DIR())
        os.unlink(service)


def restart_as_sudo():
    print(
        """Switching to root user to uninstall web services \n\n
        (you will be prompted for your password)"""
    )
    run(
        "sudo python3 -m loophost.uninstall",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    print("Uninstall finished.")
    run("""/usr/bin/open "https://loophost.dev/exit_survey.html" """, shell=True)
    sys.exit()


if __name__ == "__main__":
    # TODO: Make this impotent and reentrant safe
    if os.geteuid() == 0:
        uninstall_two()
    else:
        uninstall_one()
