import getpass
import platform
from loophost.installer import post_install_two, step_two_as_root
from pyuac import main_requires_admin

@main_requires_admin
def win_main():
    post_install_two()


if __name__ == "__main__":
    if platform.system().lower().startswith('win'):
        print("This step has to be run as Admin...")
        win_main()
    elif getpass.getuser() not in ["root"]:
        step_two_as_root()
    else:
        post_install_two()
