from typing import Tuple, Dict, Any

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from application.blacklist import BLACKLIST
from auth.schemas import LoginSchema
from flask import request

from users.models import UserModel
from utils.constants import (
    EMAIL_DOES_NOT_EXISTS,
    EMAIL_NOT_ACTIVE_USER,
    PW_DO_NOT_MATCH,
)
from utils.custom_exceptions import SearchException, InvalidCredentials
from utils.utils import check_password

login_schema = LoginSchema()


def login_user() -> Tuple[Dict[str, Any], int]:
    """Log in user to the system with email and password

    :return: Tuple with a dictionary that contains "data" with
     'access_token', 'refresh_token', 'user_email' and status code
    """

    user_json = request.get_json()
    loaded_user = login_schema.load(user_json)
    user = UserModel.get_by_email(loaded_user["email"])
    if not user:
        raise SearchException(
            EMAIL_DOES_NOT_EXISTS.format(loaded_user["email"])
        )
    if not user.is_active:
        raise SearchException(EMAIL_NOT_ACTIVE_USER(user.email))
    if not check_password(loaded_user["password"], user.password):
        raise InvalidCredentials(PW_DO_NOT_MATCH)
    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(user.id)
    return {
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": login_schema.dump(loaded_user),
        }
    }, 200


@jwt_required()
def logout_user() -> Tuple[Dict[str, Any], int]:
    """Logout user from the system, adding access_token to the BLACKLIST

    :return: Tuple with a dictionary that contains "status message" and status code
    """
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return {"message": "Successfully logged out"}, 200


@jwt_required(refresh=True)
def refresh() -> Tuple[Dict[str, Any], int]:
    """Refreshes expired access_token for User

    :return: Tuple with a dictionary that contains "data" with
     the access token for the User
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return {"data": {"access_token": access_token}}, 200
