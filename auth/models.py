from sqlalchemy import exc

from application import db
from utils.constants import SOMETHING_WENT_WRONG


class TokenBlocklistModel(db.Model):
    jti = db.Column(db.String(36), nullable=False, primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    @classmethod
    def get_by_jti(cls, jti):
        return cls.query.filter_by(jti=jti).scalar()

    def save_to_db(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            raise exc.SQLAlchemyError(SOMETHING_WENT_WRONG.format(str(err)))
