"""Loophost administration web app.
This runs as a launchd-dispatched python web app.
It displays a web-based administration screen.
Must be run with a CWD of the .loophost folder.
"""

import os
import json
import pathlib
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


admin = Flask(__name__)
csrf = CSRFProtect(admin)
bootstrap = Bootstrap5(admin)
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(admin)
admin.register_blueprint(start, url_prefix="/start")  # unused but I need the templates


@cache.cached(timeout=3600)
def latest_version():
    return has_update(repo="loophost", at="pip", current_version=__version__)


@admin.context_processor
def inject_globals():
    return dict(NEW_VERSION=latest_version())


@admin.route("/unbind")
def unbind():
    project = request.args.get("project")
    if project and project in config["apps"]:
        del config["apps"][project]
        with open(DATA_FILE_PATH(), "w+") as appjson:
            appjson.write(json.dumps(config))
    return redirect("/")


@admin.route("/share")
def share():
    project = request.args.get("project")
    if not project:
        return redirect("/")
    target = pathlib.Path(
        pathlib.Path.home(),
        "Library",
        "LaunchAgents",
        f"dev.fling.hub.ssh.{project}.plist",
    )

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

    if project and project in config.get("share", {}):
        del config["share"][project]
        unregister_tunnel(target)
    elif project:
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
    if request.form.get("application_port"):
        config["apps"][project] = request.form.get("application_port")
        with open(DATA_FILE_PATH(), "w+") as appjson:
            appjson.write(json.dumps(config))

    return render_template(
        "local.html",
        config=config,
        apps=config["apps"],
        share=config.get("share"),
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

