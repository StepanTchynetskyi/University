import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import exc

from application.db import db


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
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

    def save_to_db(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            return str(err)
        return False

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()
