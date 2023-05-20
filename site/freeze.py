from flask_frozen import Freezer
from app import app

freezer = Freezer(app)
app.config['FREEZER_DEFAULT_MIMETYPE'] = 'text/html'

if __name__ == '__main__':
    freezer.freeze()
