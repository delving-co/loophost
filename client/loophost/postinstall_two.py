import getpass
import platform
from loophost.installer import step_two_win, step_two_mac, step_two_linux, step_two_as_root
from pyuac import main_requires_admin


@main_requires_admin
def win_main():
    step_two_win()


if __name__ == "__main__":
    if platform.system().lower().startswith('win'):
        print("This step has to be run as Admin...")
        win_main()
    elif getpass.getuser() not in ["root"]:
        step_two_as_root()
    else:
        if "linux" in platform.system().lower():
            step_two_linux()
        else:
            step_two_mac()
