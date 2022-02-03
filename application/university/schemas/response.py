# base response {{"message", status_code}, data , errors}

from marshmallow import Schema, fields


class BaseResponse(Schema):
    class Meta:
        ordered = True

    status = fields.Dict()
    data = fields.List(fields.Dict())
    errors = fields.List(fields.Dict())
