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
from application.university.models.specialty import SpecialtyModel
from application.university.models.group import GroupModel
from application.university.models.subject import SubjectModel
from application.university.resources.user import user_blprnt
from application.university.resources.position import position_blprnt
from application.university.resources.specialty import specialty_blprnt


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
    app.register_blueprint(position_blprnt)
    app.register_blueprint(specialty_blprnt)
