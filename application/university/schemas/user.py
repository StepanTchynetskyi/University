from marshmallow import EXCLUDE
from application.ma import ma
from application.university.models.user import (
    UserModel,
    StudentModel,
    TeacherModel,
)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        unknown = EXCLUDE
        load_only = ("password",)


class StudentSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested(UserSchema, many=False)

    class Meta:
        model = StudentModel
        load_instance = True
        unknown = EXCLUDE
        include_fk = True
        dump_only = ("id",)


class TeacherSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested(UserSchema, many=False)

    class Meta:
        model = TeacherModel
        load_instance = True
        unknown = EXCLUDE
        include_fk = True
