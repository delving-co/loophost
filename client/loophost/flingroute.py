"""Loophost administration web app.
This runs as a launchd-dispatched python web app.
It displays a web-based administration screen.
Must be run with a CWD of the .loophost folder.
"""

import os
import sys
import json
import pathlib
from fling import start as startmod
from fling.start import start
from flask import Flask, request, render_template, redirect
from flask_bootstrap import Bootstrap5
from flask_caching import Cache
from loophost.launchd_plist import register_tunnel, unregister_tunnel, generate_keys
from loophost import HUBDIR, __version__, DATA_FILE_PATH
from lastversion import has_update
from fling_cli import get_fling_client
from fling_client.api.loophost import expose_app_expose_app_put
from flask_wtf.csrf import CSRFProtect


config = json.loads(pathlib.Path.read_text(DATA_FILE_PATH()))

admin = None
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    admin = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    admin = Flask(__name__)

admin.config["SECRET_KEY"] = config.get('SECRET_KEY', 'foobar')
csrf = CSRFProtect(admin)
bootstrap = Bootstrap5(admin)
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(admin)


@cache.cached(timeout=3600)
def latest_version():
    return has_update(repo="loophost", at="pip", current_version=__version__)


@admin.context_processor
def inject_globals():
    return dict(NEW_VERSION=latest_version())


def setup_tunnel_keys(project):
    if not os.path.exists("tunnelkey.pub"):
        # TODO(JMC): Don't do this so often
        fling_client = get_fling_client(require_auth=True)
        pub, priv = generate_keys()
        with open("tunnelkey.pub", "w+") as pubfile:
            pubfile.write(pub)
        with open("tunnelkey", "w+") as privfile:
            privfile.write(priv)
        os.chmod("tunnelkey", 0o600)
        expose_app_expose_app_put.sync(
            client=fling_client, app_name=project, ssh_public_key=pub
        )


def unbind(project):
    del config["apps"][project]
    with open(DATA_FILE_PATH(), "w+") as appjson:
        appjson.write(json.dumps(config))
    return


def share(project):
    target = pathlib.Path(
        pathlib.Path.home(),
        "Library",
        "LaunchAgents",
        f"dev.fling.hub.ssh.{project}.plist",
    )

    if project and project in config.get("share", {}):
        del config["share"][project]
        unregister_tunnel(target)
    elif project:
        setup_tunnel_keys(project)
        if not config.get("share"):
            config["share"] = {}
        config["share"][project] = "public"
        register_tunnel(
            project, pathlib.Path(HUBDIR, "plist", "ssh.plist.template"), target
        )
    with open(DATA_FILE_PATH(), "w+") as appjson:
        appjson.write(json.dumps(config))
    return redirect(f"/config/{project}")


@admin.route("/config/<project>", methods=["GET", "POST"])
def config_page(project):
    if project and project in config["apps"]:
        print(f"Updating config for {project} with action {request.form.get('action')}")
        if request.form.get("action") == "unbind":
            unbind(project)
            return redirect("/")
        elif request.form.get("action") == "share":
            share(project)
    if request.form.get("application_port") and not request.form.get("action"):
        config["apps"][project] = request.form.get("application_port")
        with open(DATA_FILE_PATH(), "w+") as appjson:
            appjson.write(json.dumps(config))

    return render_template(
        "local.html",
        config=config,
        apps=config["apps"],
        share=config.get("share", {}),
        project=project,
    )


@admin.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@admin.route("/<path:path>", methods=["GET", "POST"])
def admin_page(path):
    fqdn = request.host.split(".")
    if len(fqdn) < 4:
        return render_template(
            "admin.html",
            config=config,
            apps=config["apps"],
            share=config.get("share"),
            fqdn=".".join(fqdn),
        )
    project = fqdn.pop(0)
    return redirect(f"https://{config['fqdn']}/config/{project}")


if __name__ == "__main__":
    # admin.run(host=f"unix://{os.getcwd()}/loophost.soc")
    admin.run(host=f"0.0.0.0", port=5816)

