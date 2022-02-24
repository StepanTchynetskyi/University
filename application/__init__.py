import os
from flask import Flask
from flask_jwt_extended import JWTManager
from application.db import db, migrate
from application.ma import ma
from users import models as user_models
from positions import models as position_models
from groups import models as group_models
from specialties import models as specialty_models
from subjects import models as subject_models
from assignments import models as assignment_models
from auth import models as auth_models


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
    def check_if_token_revoked(jwt_headers, jwt_data):
        jti = jwt_data["jti"]
        token = auth_models.TokenBlocklistModel.get_by_jti(jti)
        return token is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        return {
            "errors": {"TokenException": "The token has been revoked."}
        }, 401

    register_blueprints(app)
    # print(app.url_map)
    return app


def register_blueprints(app):
    from users import urls as user_urls
    from subjects import urls as subject_urls
    from positions import urls as position_urls
    from groups import urls as group_urls
    from auth import urls as auth_urls
    from specialties import urls as specialty_urls
    from assignments import urls as assignment_urls

    app.register_blueprint(user_urls.mod)
    app.register_blueprint(group_urls.mod)
    app.register_blueprint(specialty_urls.mod)
    app.register_blueprint(subject_urls.general_mod)
    app.register_blueprint(auth_urls.mod)
    app.register_blueprint(assignment_urls.general_mod)
