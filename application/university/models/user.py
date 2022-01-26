import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import exc
from application import db
from application.university.utils.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
)


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(MAX_EMAIL_LENGTH), nullable=False, unique=True)
    first_name = db.Column(db.String(MAX_FIRST_NAME_LENGTH), nullable=False)
    last_name = db.Column(db.String(MAX_LAST_NAME_LENGTH), nullable=False)
    password = db.Column(db.String(MAX_PASSWORD_LENGTH), nullable=False)
    age = db.Column(db.SmallInteger)
    is_active = db.Column(db.Boolean, default=True)
    student = db.relationship(
        "StudentModel", uselist=False, cascade="all,delete", backref="user"
    )
    teacher = db.relationship(
        "TeacherModel", uselist=False, cascade="all,delete", backref="user"
    )

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class StudentModel(db.Model):
    __tablename__ = "student"
    id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(UserModel.id, ondelete="CASCADE"),
        primary_key=True,
    )
    year_of_study = db.Column(db.SmallInteger, nullable=False)

    def remove_from_db(self, user):
        db.session.delete(self)
        db.session.delete(user)
        db.session.commit()

    @classmethod
    def get_by_id(cls, student_id):
        return cls.query.filter_by(id=student_id).first()

    @classmethod
    def get_all_students(cls):
        return cls.query.all()


class TeacherModel(db.Model):
    __tablename__ = "teacher"
    id = db.Column(
        UUID(as_uuid=True), db.ForeignKey(UserModel.id), primary_key=True
    )
    position_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("position.id"), nullable=False
    )


def save_to_db(specific_user):
    db.session.add(specific_user)
    try:
        db.session.commit()
    except exc.SQLAlchemyError as err:
        db.session.rollback()
        return str(err)
    return False


def commit_specific_user(user, specific_user):
    try:
        db.session.add_all([user, specific_user])
        db.session.commit()
    except exc.SQLAlchemyError as err:
        db.session.rollback()
        return str(err)
    return False
