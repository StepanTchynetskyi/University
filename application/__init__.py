import os
from flask import Flask
from application.db import db, migrate
from application.ma import ma
from application.university.models.user import (
    UserModel,
    StudentModel,
    TeacherModel,
)
from application.university.models.position import PositionModel
from application.university.resources.user import user_blprnt


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

    register_blueprints(app)
    return app


def register_blueprints(app):
    app.register_blueprint(user_blprnt)
