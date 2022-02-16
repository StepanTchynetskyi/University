from sqlalchemy.dialects.postgresql import UUID, VARCHAR
from application.db import db
from utils.base_model import BaseModel
from utils.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH,
)


class UserModel(BaseModel):
    __tablename__ = "user"

    email = db.Column(db.String(MAX_EMAIL_LENGTH), nullable=False, unique=True)
    first_name = db.Column(db.String(MAX_FIRST_NAME_LENGTH), nullable=False)
    last_name = db.Column(db.String(MAX_LAST_NAME_LENGTH), nullable=False)
    password = db.Column(VARCHAR(), nullable=False)
    age = db.Column(db.SmallInteger)
    is_active = db.Column(db.Boolean, default=True)
    type = db.Column(db.String(MAX_FIRST_NAME_LENGTH))

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "user",
        "with_polymorphic": "*",
    }

    @classmethod
    def get_all_records(cls):
        return cls.query.filter_by(is_active=True)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class StudentModel(UserModel):
    __tablename__ = "student"

    id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(UserModel.id, ondelete="CASCADE"),
        primary_key=True,
    )
    year_of_study = db.Column(db.SmallInteger, nullable=False)
    __mapper_args__ = {"polymorphic_identity": "student"}


class TeacherModel(UserModel):
    __tablename__ = "teacher"

    id = db.Column(
        UUID(as_uuid=True), db.ForeignKey(UserModel.id), primary_key=True
    )
    position_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("position.id", ondelete="SET NULL"),
        nullable=False,
    )
    position = db.relationship(
        "PositionModel", uselist=False, back_populates="teachers"
    )
    specialty = db.relationship(
        "SpecialtyModel",
        uselist=False,
        cascade="all,delete",
        backref="teacher",
    )
    group = db.relationship(
        "GroupModel",
        cascade="all,delete",
        backref="teacher",
    )
    __mapper_args__ = {"polymorphic_identity": "teacher"}
