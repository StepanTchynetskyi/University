from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from users import models as user_models
from utils.constants import (
    HAS_UPPERCASE_LETTERS,
    HAS_LOWERCASE_LETTERS,
    HAS_NUMBERS,
    HAS_SYMBOLS,
    VALIDATE_EMAIL,
)


class UserValidation:
    @validates("first_name")
    def validate_first_name(self, value):
        if len(value) < 2:
            raise ValidationError("Too short first name (min 2 symbols)")

    @validates("last_name")
    def validate_last_name(self, value):
        if len(value) < 2:
            raise ValidationError("Too short last name (min 2 symbols)")

    @validates("email")
    def validate_email(self, value):
        if not VALIDATE_EMAIL.fullmatch(value):
            raise ValidationError("Invalid Email Address")

    @validates("password")
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Too short password(min 8 symbols)")
        elif not HAS_UPPERCASE_LETTERS.search(value):
            raise ValidationError(
                "Password should have at least one uppercase letter"
            )
        elif not HAS_LOWERCASE_LETTERS.search(value):
            raise ValidationError(
                "Password should have at least one lowercase letter"
            )
        elif not HAS_NUMBERS.search(value):
            raise ValidationError("Password should have at least one number")
        elif not HAS_SYMBOLS.search(value):
            raise ValidationError(
                "Password should have at least one special symbol"
            )

    @validates("age")
    def validate_age(self, value):
        if value < 1:
            raise ValidationError("Age Should Be Positive Number")
        elif value > 130:
            raise ValidationError("Too Big Number Provided For Age")


class UserSchema(ma.SQLAlchemyAutoSchema, UserValidation):
    class Meta:
        model = user_models.UserModel
        load_instance = True
        unknown = EXCLUDE
        load_only = ("password",)
        dump_only = ("id", "created_on", "updated_on")


class StudentSchema(ma.SQLAlchemyAutoSchema, UserValidation):
    groups = ma.Nested("GroupSchema", many=True)

    class Meta:
        model = user_models.StudentModel
        load_instance = True
        unknown = EXCLUDE
        include_fk = True
        load_only = ("password",)
        dump_only = ("id", "is_active", "created_on", "updated_on")

    @validates("year_of_study")
    def validate_year_of_study(self, value):
        if value < 1 or value > 8:
            raise ValidationError("Year of Study should be between 1 and 8")


class TeacherSchema(ma.SQLAlchemyAutoSchema, UserValidation):
    position = ma.Nested("PositionSchema", many=False, exclude=("teachers",))
    specialty = ma.Nested(
        "SpecialtySchema", many=False, exclude=("teacher", "teacher_id")
    )

    subjects = ma.Nested("SubjectSchema", many=True, exclude=("teachers",))

    class Meta:
        model = user_models.TeacherModel
        load_instance = True
        unknown = EXCLUDE
        include_fk = True
        load_only = ("password",)
        dump_only = ("id", "is_active", "created_on", "updated_on")
