"""Offloading proxy.
This runs inside the main uWSGI process and sends offload headers
for each registered app. For unregistered apps, it displays a 
web-based administration screen."""

import os
import json
from flask import Flask, request, render_template, redirect


config = None
with open("/etc/flingdev/loophost.json") as appjson:
    config = json.loads(appjson.read())


# logo = None
# logo_path = "logo-hc.txt"
# with open(logo_path, "r") as logo_file:
#     logo = logo_file.read()

logo = "FLING"

admin = Flask(__name__, static_url_path="/dontdoit")


@admin.route("/unbind")
def unbind():
    project = request.args.get("project")
    if project and project in config["apps"]:
        del config["apps"][project]
        with open("loophost.json", "w") as appjson:
            appjson.write(json.dumps(config))
    return redirect("/")


@admin.route("/", defaults={'path': ''}, methods=["GET", "POST"])
@admin.route("/<path:path>", methods=["GET", "POST"])
def admin_page(path):
    fqdn = request.host.split(".")
    if len(fqdn) < 4:
        return render_template("admin.html", apps=config["apps"], fqdn=".".join(fqdn))
    project = fqdn.pop(0)
    if request.form.get("application_port"):
        config["apps"][project] = request.form.get("application_port")
        with open("loophost.json", "w") as appjson:
            appjson.write(json.dumps(config))
    return render_template(
        "local.html",
        logo=logo.encode("ascii", "xmlcharrefreplace").decode(),
        apps=config["apps"],
        project=project,
        fqdn=".".join(fqdn),
    )


def offload_proxy(env, start_response):
    headers = []
    project = env.get("HTTP_HOST", "firstapp.bar").split(".")[0]
    if project in ['localhost', '127']:
        project = "firstapp"
    if config["fqdn"] not in env["HTTP_HOST"]:
        start_response('302 Found', [('Location', f"https://{project}.{config['fqdn']}")])
        return [b'1']
    offload = config["apps"].get(project, None)
    if offload and (not offload.startswith("/") or os.path.exists(offload)):
        headers.append(("X-Offload-to-SSE", offload))
        start_response("200 OK", headers)
        return [b'']
    print(env['wsgi.input'])
    return admin(env, start_response)


application = offload_proxy
