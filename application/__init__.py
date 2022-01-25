import os
from flask import Flask


def create_app(test_config=None):
    """Factory to create the Flask application
    :return: A `Flask` application instance
    """
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    return app
