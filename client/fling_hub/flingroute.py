"""Offloading proxy.
This runs inside the main uWSGI process and sends offload headers
for each registered app. For unregistered apps, it displays a
web-based administration screen.

Must be run within the .flingdev folder in the user's home directory.
"""

import os
import json
from fling.start import start
from flask import Flask, request, render_template, redirect
from flask_bootstrap import Bootstrap5
from flask_caching import Cache
from . import __version__
from lastversion import has_update
from os import environ


config = None
with open("loophost.json") as appjson:
    config = json.loads(appjson.read())


admin = Flask(__name__)
bootstrap = Bootstrap5(admin)
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(admin)
admin.register_blueprint(start, url_prefix="/start")  # unused but I need the templates


@cache.cached(timeout=3600)
def latest_version():
    return has_update(repo="fling-hub", at="pip", current_version=__version__)


@admin.context_processor
def inject_globals():
    return dict(NEW_VERSION=latest_version())


@admin.route("/unbind")
def unbind():
    project = request.args.get("project")
    if project and project in config["apps"]:
        del config["apps"][project]
        with open("loophost.json", "w") as appjson:
            appjson.write(json.dumps(config))
    return redirect("/")


@admin.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@admin.route("/<path:path>", methods=["GET", "POST"])
def admin_page(path):
    fqdn = request.host.split(".")
    if len(fqdn) < 4:
        return render_template(
            "admin.html", apps=config["apps"], sharing={}, fqdn=".".join(fqdn)
        )
    project = fqdn.pop(0)
    if request.form.get("application_port"):
        config["apps"][project] = request.form.get("application_port")
        with open("loophost.json", "w") as appjson:
            appjson.write(json.dumps(config))
        return redirect(f"https://{project}.{'.'.join(fqdn)}")
        # return redirect(f"""<html><head>
        #                 <meta http-equiv="refresh" 
        #                     content="2;URL='https://{project}.{'.'.join(fqdn)}'/>
        #                 </head><body>Redirecting...</body></html>""")
    return render_template(
        "local.html",
        apps=config["apps"],
        sharing={},
        project=project,
        fqdn=".".join(fqdn),
    )


if __name__ == "__main__":
    admin.run(host=f"unix://{os.getcwd()}/loophost.soc")
