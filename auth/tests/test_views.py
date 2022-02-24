import json
import unittest
import uuid
from unittest.mock import patch

from flask_jwt_extended import create_refresh_token, get_jwt
from marshmallow import ValidationError

from users import models as user_models
from utils.constants import (
    EMAIL_DOES_NOT_EXISTS,
    PW_DO_NOT_MATCH,
    EMAIL_NOT_ACTIVE_USER,
)
from utils.custom_exceptions import SearchException, InvalidCredentials
from utils.test_utils import BaseTestCase, create_obj, get_headers
from utils.utils import get_hashed_password


class AuthTestCase(BaseTestCase):
    data = {
        "email": "studw@gmail.com",
        "first_name": "stud",
        "last_name": "student1",
        "password": "Awnafjfawga12@",
        "age": 18,
        "year_of_study": 2,
    }
    student_id, student = create_obj(data, user_models.StudentModel)
    student.is_active = True
    student.password = get_hashed_password(
        student.password.encode("utf8")
    ).decode("utf-8")

    @patch("users.models.UserModel.get_by_email")
    def test_login_user_success(self, mock_user_get_by_email):
        mock_user_get_by_email.return_value = self.student
        data = {"email": "studw@gmail.com", "password": "Awnafjfawga12@"}
        response = self.client.post("auth/login", json=data)
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["user"]["email"], data["email"])
        self.assertTrue(response_data["access_token"])
        self.assertTrue(response_data["refresh_token"])

    def test_login_user_fail_wrong_email(self):
        data = {"email": "studgmail.com", "password": "Awnafjfawga12@"}
        with self.assertRaises(ValidationError) as context:
            self.client.post("auth/login", json=data)
        message = "{'email': ['Invalid Email Address']}"
        self.assertEqual(str(context.exception), message)

    @patch("users.models.UserModel.get_by_email")
    def test_login_user_fail_user_not_found(self, mock_user_get_by_email):
        mock_user_get_by_email.return_value = None
        data = {"email": "studw1@gmail.com", "password": "Awnafjfawga12@"}
        with self.assertRaises(SearchException) as context:
            self.client.post("auth/login", json=data)
        self.assertEqual(
            str(context.exception), EMAIL_DOES_NOT_EXISTS.format(data["email"])
        )

    @patch("users.models.UserModel.get_by_email")
    def test_login_user_fail_user_not_active(self, mock_user_get_by_email):
        mock_user_get_by_email.return_value = self.student
        self.student.is_active = False
        data = {"email": "studw@gmail.com", "password": "Awnafjfawga12@"}
        with self.assertRaises(SearchException) as context:
            self.client.post("auth/login", json=data)
        self.assertEqual(
            str(context.exception), EMAIL_NOT_ACTIVE_USER.format(data["email"])
        )
        self.student.is_active = True

    @patch("users.models.UserModel.get_by_email")
    def test_login_user_fail_wrong_password(self, mock_user_get_by_email):
        mock_user_get_by_email.return_value = self.student
        data = {"email": "studw@gmail.com", "password": "Awnafjfawga122@"}
        with self.assertRaises(InvalidCredentials) as context:
            self.client.post("auth/login", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)

    def test_login_user_fail_missing_required_fields(self):
        data = {
            "email": "studw@gmail.com",
        }
        with self.assertRaises(ValidationError) as context:
            self.client.post("auth/login", json=data)
        message = "{'password': ['Missing data for required field.']}"
        self.assertEqual(str(context.exception), message)
        data = {"password": "Awnafjfawga12@"}
        with self.assertRaises(ValidationError) as context:
            self.client.post("auth/login", json=data)
        message = "{'email': ['Missing data for required field.']}"
        self.assertEqual(str(context.exception), message)

    @patch("auth.models.TokenBlocklistModel.get_by_jti")
    @patch("auth.models.TokenBlocklistModel.save_to_db")
    def test_logout_user(
        self, mock_blocklist_save_to_db, mock_blocklist_get_by_jti
    ):
        mock_blocklist_save_to_db.return_value = None
        mock_blocklist_get_by_jti.return_value = None
        headers = get_headers(self.student.id)
        response = self.client.post("auth/logout", headers=headers)
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(message, "Successfully logged out")
        mock_blocklist_get_by_jti.return_value = uuid.uuid4()
        response = self.client.post("auth/logout", headers=headers)
        message = json.loads(response.data.decode("utf-8"))["errors"]
        self.assertDictEqual(
            message, {"TokenException": "The token has been revoked."}
        )

    def test_refresh_token(self):
        refresh_token = create_refresh_token(self.student_id)
        headers = {"Authorization": "Bearer {}".format(refresh_token)}
        response = self.client.post("auth/refresh", headers=headers)
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data["access_token"])

    def test_refresh_token_fail(self):
        response = self.client.post("auth/refresh")
        msg = json.loads(response.data.decode("utf-8"))["msg"]
        self.assertEqual(response.status_code, 401)
        self.assertEqual(msg, "Missing Authorization Header")


if __name__ == "__main__":
    unittest.main()
