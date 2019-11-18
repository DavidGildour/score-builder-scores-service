import os
import sys

from app import app
from db import db


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    app.config.from_object('config.DevelopmentConfig')
    db.init_app(app)

    if len(sys.argv) > 1:
        if sys.argv[1] == 'docker':
            app.run(debug=True, port=5002, host='0.0.0.0')
        elif sys.argv[1] == 'default':
            os.environ['FLASK_ENV'] = 'development'
            app.run(debug=True, port=5002)
        else:
            print('Unknown command: {}'.format(sys.argv[1]))
    else:
        os.environ['FLASK_ENV'] = 'development'
        app.run(debug=True, port=5002)
