from flask_frozen import Freezer
from app import app

freezer = Freezer(app)
app.config["FREEZER_DEFAULT_MIMETYPE"] = "text/html"


@freezer.register_generator
def extra_url_generator():
    yield "/exit_survey.html"


if __name__ == "__main__":
    freezer.freeze()
