from marshmallow import Schema, fields


class BaseResponse(Schema):
    class Meta:
        ordered = True

    status = fields.Dict()
    data = fields.Raw(required=False)
    errors = fields.List(fields.Dict(), required=False)
