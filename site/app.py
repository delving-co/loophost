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


@app.route("/upgrade.html")
def upgrade():
    return render_template("upgrade.html")


@app.route("/update.html")
def upgrade():
    return render_template("update.html")


@app.route("/tech.html")
def tech():
    return render_template("tech.html")


@app.route("/install.sh")
def install_script():
    return send_file("static/install.sh", "text/plain")


start_app(main, domain_name=domain_name, default_routes=False)
