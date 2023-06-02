import shutil
from loophost import GET_LOOPHOST_DIR
from subprocess import run
from loophost import fill_template


def register_launchd_service(project, template_path, target_path):
    TARGET_DIR = GET_LOOPHOST_DIR()
    fill_template(template_path, target_path, project)
    run(["launchctl", "unload", target_path], cwd=TARGET_DIR)
    run(["launchctl", "load", target_path], cwd=TARGET_DIR)


def unregister_launchd_service(target_path):
    run(["launchctl", "unload", target_path], cwd=GET_LOOPHOST_DIR())
    shutil.rmtree(target_path, ignore_errors=True)
