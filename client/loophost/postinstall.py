import sys
from loophost import store_localuser
from loophost.installer import (
    open_loophost,
    step_one_win,
    step_one_mac,
    step_one_linux,
    step_two_as_root,
    authenticate_with_fling,
    create_update_loophost_json,
)
import platform


def post_install():
    store_localuser()
    authenticate_with_fling()
    create_update_loophost_json()
    system = platform.system().lower()
    if "darwin" in system:
        step_one_mac()
    elif "win" in system:
        step_one_win()
    else:
        step_one_linux()
    step_two_as_root()
    open_loophost()
    print("All finished.")
    sys.exit()


if __name__ == "__main__":
    print("Installing LoopHost...")
    post_install()
