from marshmallow import EXCLUDE, Schema, fields, validates, ValidationError

from application.ma import ma
from auth import models as auth_models
from utils.constants import VALIDATE_EMAIL


class LoginSchema(Schema):

    email = fields.String(required=True)
    password = fields.String(required=True)

    class Meta:
        load_only = ("password",)

    @validates("email")
    def validate_email(self, value):
        if not VALIDATE_EMAIL.fullmatch(value):
            raise ValidationError("Invalid Email Address")

    @validates("password")
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Too short password(min 8 symbols)")


class TokenBlocklistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = auth_models.TokenBlocklistModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = "created_on"
