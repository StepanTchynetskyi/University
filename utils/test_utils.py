import unittest
import uuid

from flask_jwt_extended import create_access_token

from application import create_app


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.ctx.pop()


def get_headers(user_id):
    access_token = create_access_token(identity=user_id, fresh=True)
    headers = {"Authorization": "Bearer {}".format(access_token)}
    return headers


def create_obj(data, model):
    obj_id = uuid.uuid4()
    obj = model()
    obj.id = obj_id
    for key, value in data.items():
        setattr(obj, key, value)
    return obj_id, obj
