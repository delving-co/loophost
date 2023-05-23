from fling.start import app, start_app, Bootstrap5, Admin
from fling import start
from flask import render_template, send_file
from pprint import pprint


print(start.__file__)

domain_name = "loophost.dev"


def main():
    return ""


@app.route("/")
def main_index():
    return render_template("index.html")


@app.route("/<page>.html")
def upgrade(page):
    return render_template(f"{page}.html")


@app.route("/install.sh")
def install_script():
    return send_file("static/install.sh", "text/plain")


start_app(main, domain_name=domain_name, default_routes=False)
