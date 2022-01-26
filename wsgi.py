from flask import jsonify
from marshmallow import ValidationError

from application import create_app

app = create_app()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400
