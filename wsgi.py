import json
from marshmallow import ValidationError
from sqlalchemy import exc
from application import create_app
from utils.schemas.response import BaseResponse
from utils.custom_exceptions import (
    SearchException,
    CreateException,
    NotProvided,
    InvalidCredentials,
    UpdateException,
)

app = create_app()

response_schema = BaseResponse()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return {"errors": err.messages}, 400


@app.errorhandler(SearchException)
def handle_search_exception(err):
    return {"errors": {err.__class__.__name__: str(err)}}, err.status_code


@app.errorhandler(CreateException)
def handle_create_exception(err):
    return {"errors": {err.__class__.__name__: str(err)}}, 400


@app.errorhandler(exc.SQLAlchemyError)
def handle_sqlalchemy_errror(err):
    return {"errors": {err.__class__.__name__: str(err)}}, 400


@app.errorhandler(PermissionError)
def handle_permission_error(err):
    return {"errors": {err.__class__.__name__: str(err)}}, 403


@app.errorhandler(NotProvided)
def handle_not_provided_error(err):
    return {"errors": {err.__class__.__name__: str(err)}}, err.status_code


@app.errorhandler(InvalidCredentials)
def handle_invalid_credentials(err):
    return {"errors": {err.__class__.__name__: str(err)}}, err.status_code


@app.errorhandler(UpdateException)
def handle_update_exception(err):
    return {"errors": {err.__class__.__name__: str(err)}}, err.status_code


@app.errorhandler(ValueError)
def handle_value_error(err):
    return {"errors": {err.__class__.__name__: str(err)}}, 400


@app.after_request
def form_response(response):
    response_json = response.get_json()
    if not response_json:
        return response
    message = response_json.get("message", None)
    message = message if message else response._status
    result_json = {
        "status": {"message": message, "code": response._status_code}
    }
    data = response_json.get("data", None)
    if data:
        result_json["data"] = data
    errors = response_json.get("errors", None)
    if errors:
        errors = errors if isinstance(errors, list) else [errors]
        result_json["errors"] = errors
    processed_response = response_schema.load(result_json)
    response.data = json.dumps(response_schema.dump(processed_response))
    return response
