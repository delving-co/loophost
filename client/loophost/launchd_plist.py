from io import StringIO
import pathlib
import shutil
from loophost import LOOPHOST_DOMAIN, TUNNEL_DOMAIN, PYEX, HUBDIR, GET_FLINGUSER_NAME, GET_LOOPHOST_DIR
from string import Template
from subprocess import run
import paramiko


def generate_keys():
    key = paramiko.RSAKey.generate(2048)
    privateString = StringIO()
    key.write_private_key(privateString)
    return f"{key.get_name()} {key.get_base64()}", privateString.getvalue()


def register_tunnel(project, template_path, target_path):
    TARGET_DIR = GET_LOOPHOST_DIR()
    shutil.copy2(template_path, TARGET_DIR)

    d = {"CWD": TARGET_DIR,
         "USERNAME": GET_FLINGUSER_NAME(),
         "PYEX": PYEX,
         "HUBDIR": HUBDIR,
         "LOOPHOST_DOMAIN": LOOPHOST_DOMAIN,
         "TUNNEL_DOMAIN": TUNNEL_DOMAIN,
         "LOCAL_USER": pathlib.Path('localuser.txt').read_text().strip(),
         "PROJECT": project}

    with open(template_path, "r") as f:
        src = Template(f.read())
        result = src.substitute(d)
        with open(target_path, "w+") as o:
            o.write(result)

    run(["launchctl", "unload", target_path], cwd=TARGET_DIR)
    run(["launchctl", "load", target_path], cwd=TARGET_DIR)


def unregister_tunnel(target_path):
    run(["launchctl", "unload", target_path], cwd=GET_LOOPHOST_DIR())
    shutil.rmtree(target_path, ignore_errors=True)
