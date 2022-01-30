from sqlalchemy import exc
from sqlalchemy.dialects.postgresql import UUID

from application.db import db
from application.university.utils.base_model import BaseModel
from application.university.utils.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
)


class UserModel(BaseModel):
    __tablename__ = "user"

    email = db.Column(db.String(MAX_EMAIL_LENGTH), nullable=False, unique=True)
    first_name = db.Column(db.String(MAX_FIRST_NAME_LENGTH), nullable=False)
    last_name = db.Column(db.String(MAX_LAST_NAME_LENGTH), nullable=False)
    password = db.Column(db.String(MAX_PASSWORD_LENGTH), nullable=False)
    age = db.Column(db.SmallInteger)
    student = db.relationship(
        "StudentModel", uselist=False, cascade="all,delete", backref="user"
    )
    teacher = db.relationship(
        "TeacherModel", uselist=False, cascade="all,delete", backref="user"
    )

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class StudentModel(BaseModel):
    __tablename__ = "student"

    id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(UserModel.id, ondelete="CASCADE"),
        primary_key=True,
    )
    is_active = db.Column(db.Boolean, default=True)
    year_of_study = db.Column(db.SmallInteger, nullable=False)

    @classmethod
    def get_all_records(cls):
        return cls.query.filter_by(is_active=True)

    def remove_from_db(self):
        teacher = TeacherModel.get_by_id(self.id)
        if teacher:
            db.session.delete(teacher)
        db.session.delete(self)
        db.session.delete(self.user)
        db.session.commit()


class TeacherModel(BaseModel):
    __tablename__ = "teacher"

    id = db.Column(
        UUID(as_uuid=True), db.ForeignKey(UserModel.id), primary_key=True
    )
    is_active = db.Column(db.Boolean, default=True)
    position_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("position.id", ondelete="SET NULL"),
        nullable=False,
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

    @classmethod
    def get_all_records(cls):
        return cls.query.filter_by(is_active=True)

    def remove_from_db(self):
        student = StudentModel.get_by_id(self.id)
        if student:
            db.session.delete(student)
        db.session.delete(self)
        db.session.delete(self.user)
        db.session.commit()


def commit_specific_user(user, specific_user):
    try:
        db.session.add_all([user, specific_user])
        db.session.commit()
    except exc.SQLAlchemyError as err:
        db.session.rollback()
        return str(err)
    return False
