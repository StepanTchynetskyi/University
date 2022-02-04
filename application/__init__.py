import os
from flask import Flask
from flask_jwt_extended import JWTManager
from application.db import db, migrate
from application.ma import ma
from application.blacklist import BLACKLIST
from application.university.models.user import (
    UserModel,
    StudentModel,
    TeacherModel,
)
from application.university.models.position import PositionModel
from application.university.models.specialty import SpecialtyModel
from application.university.models.group import GroupModel
from application.university.models.subject import SubjectModel
from application.university.resources.user import user_blprnt, auth_blprnt
from application.university.resources.position import position_blprnt
from application.university.resources.specialty import specialty_blprnt
from application.university.resources.subject import subject_blprnt
from application.university.resources.group import group_blprnt


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ["APP_SETTINGS"])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    jwt = JWTManager(app)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    @app.before_first_request
    def create_tables():
        db.create_all()

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        pass

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_headers, jwt_data):
        return jwt_data["jti"] in BLACKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        return {"errors": "The token has been revoked."}, 401

    register_blueprints(app)
    return app


def register_blueprints(app):
    app.register_blueprint(user_blprnt)
    app.register_blueprint(position_blprnt)
    app.register_blueprint(specialty_blprnt)
    app.register_blueprint(subject_blprnt)
    app.register_blueprint(group_blprnt)
    app.register_blueprint(auth_blprnt)
