import unittest
from application import create_app


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.ctx.pop()
