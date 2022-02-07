import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import exc

from application.db import db
from application.university.utils.constants import SOMETHING_WENT_WRONG


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
    )

    @classmethod
    def get_all_records(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, searched_id):
        return cls.query.filter_by(id=searched_id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.query.filter(cls.id.in_(ids)).all()

    def save_to_db(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            raise exc.SQLAlchemyError(SOMETHING_WENT_WRONG.format(str(err)))

    def remove_from_db(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            raise exc.SQLAlchemyError(SOMETHING_WENT_WRONG.format(str(err)))
