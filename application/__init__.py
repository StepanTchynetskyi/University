import os
from flask import Flask
from application.db import db, migrate
from application.ma import ma


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ["APP_SETTINGS"])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    @app.before_first_request
    def create_tables():
        db.create_all()

    return app
