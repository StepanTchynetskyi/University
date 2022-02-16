import os
from flask import Flask
from flask_jwt_extended import JWTManager
from application.db import db, migrate
from application.ma import ma
from application.blacklist import BLACKLIST


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
        return {
            "errors": {"TokenException": "The token has been revoked."}
        }, 401

    register_blueprints(app)
    return app


def register_blueprints(app):
    from users.urls import mod as user_mod
    from positions.urls import mod as position_mod
    from groups.urls import mod as group_mod
    from auth.urls import mod as auth_mod
    from specialties.urls import mod as specialty_mod
    from subjects.urls import mod as subject_mod

    app.register_blueprint(user_mod)
    app.register_blueprint(position_mod)
    app.register_blueprint(specialty_mod)
    app.register_blueprint(subject_mod)
    app.register_blueprint(group_mod)
    app.register_blueprint(auth_mod)
