from fling.start import app, start_app
from flask import render_template, send_file


domain_name = "fling.dev"


def main():
    return ""


@app.route("/install.sh")
def install_script():
    return send_file("static/install.sh", "text/plain")


start_app(main, domain_name=domain_name)
