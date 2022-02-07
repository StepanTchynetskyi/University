import json
from marshmallow import ValidationError
from sqlalchemy import exc
from application import create_app
from application.university.schemas.response import BaseResponse
from application.university.utils.custom_exceptions import (
    SearchException,
    CreateException,
    NotProvided,
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
def handle_permission_errror(err):
    return {"errors": {err.__class__.__name__: str(err)}}, 403


@app.errorhandler(NotProvided)
def handle_not_provided_error(err):
    return {"errors": {err.__class__.__name__: str(err)}}, err.status_code


@app.after_request
def form_response(response):
    response_json = response.get_json()
    if response_json:
        data = response_json.get("data", None)
        data = data if isinstance(data, list) else [data] if data else []
        errors = response_json.get("errors", None)
        errors = (
            [errors]
            if isinstance(errors, list)
            else [errors]
            if errors
            else []
        )
        message = response_json.get("message", None)
        message = message if message else response._status
        processed_response = response_schema.load(
            {
                "status": {"message": message, "code": response._status_code},
                "data": data,
                "errors": errors,
            }
        )
        response.data = json.dumps(response_schema.dump(processed_response))
    return response
