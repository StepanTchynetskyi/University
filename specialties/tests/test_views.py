import json
import unittest
import uuid
from unittest.mock import patch

from utils import test_utils
from users import models as user_models
from specialties import models as specialty_models
from utils.constants import NOT_FOUND_BY_ID, SPECIALTY
from utils.custom_exceptions import SearchException


class SpecialtyTestCase(test_utils.BaseTestCase):
    data_teacher = {
        "email": "teacher@gmail.com",
        "first_name": "teach",
        "last_name": "teacher",
        "password": "Awnafjfawga12@",
        "age": 70,
        "is_active": True,
    }
    teacher_id, teacher = test_utils.create_obj(
        data_teacher, user_models.TeacherModel
    )
    data_specialty = {"name": "IKNI", "year": 2021, "teacher_id": teacher_id}
    specialty_id, specialty = test_utils.create_obj(
        data_specialty, specialty_models.SpecialtyModel
    )

    @patch("specialties.models.SpecialtyModel.save_to_db")
    @patch("users.models.UserModel.get_by_id")
    @patch("specialties.models.SpecialtyModel.get_by_id")
    def test_create_specialty(
        self,
        mock_specialty_get_by_id,
        mock_teacher_get_by_id,
        mock_specialty_save_to_db,
    ):
        mock_specialty_get_by_id.return_value = None
        mock_teacher_get_by_id.return_value = self.teacher
        mock_specialty_save_to_db.return_value = None
        response = self.client.post(
            "/specialties/create", json=self.data_specialty
        )
        self.assertEqual(response.status_code, 201)

    @patch("specialties.models.SpecialtyModel.get_all_records")
    def test_get_specialties(self, mock_specialty_get_all_records):
        mock_specialty_get_all_records.return_value = [self.specialty]
        response = self.client.get("/specialties")
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data["specialties"][0]["id"], str(self.specialty_id)
        )

    @patch("specialties.models.SpecialtyModel.get_by_id")
    def test_get_specialty_success(self, mock_specialty_get_by_id):
        mock_specialty_get_by_id.return_value = self.specialty
        response = self.client.get(f"/specialties/{self.specialty_id}")
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], str(self.specialty_id))

    @patch("specialties.models.SpecialtyModel.get_by_id")
    def test_get_specialty_fail(self, mock_specialty_get_by_id):
        mock_specialty_get_by_id.return_value = None
        wrong_specialty_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.get(f"/specialties/{wrong_specialty_id}")
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(SPECIALTY, wrong_specialty_id),
        )

    @patch("specialties.models.SpecialtyModel.save_to_db")
    @patch("users.models.TeacherModel.get_by_id")
    @patch("specialties.models.SpecialtyModel.get_by_id")
    def test_update_specialty_success(
        self,
        mock_specialty_get_by_id,
        mock_teacher_get_by_id,
        mock_specialty_save_to_db,
    ):
        mock_specialty_get_by_id.return_value = self.specialty
        mock_teacher_get_by_id.return_value = self.teacher
        mock_specialty_save_to_db.return_value = None
        data = {"name": "IKTA"}
        response = self.client.put(
            f"/specialties/{self.specialty_id}", json=data
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["name"], data["name"])

    @patch("specialties.models.SpecialtyModel.get_by_id")
    def test_update_specialty_fail(self, mock_specialty_get_by_id):
        mock_specialty_get_by_id.return_value = None
        data = {"name": "IKTA"}
        wrong_specialty_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.put(f"/specialties/{wrong_specialty_id}", json=data)
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(SPECIALTY, wrong_specialty_id),
        )

    @patch("specialties.models.SpecialtyModel.remove_from_db")
    @patch("specialties.models.SpecialtyModel.get_by_id")
    def test_delete_specialty_success(
        self, mock_specialty_get_by_id, mock_specialty_remove_from_db
    ):
        mock_specialty_get_by_id.return_value = self.specialty
        mock_specialty_remove_from_db.return_value = None
        response = self.client.delete(f"/specialties/{self.specialty_id}")
        self.assertEqual(response.status_code, 200)

    @patch("specialties.models.SpecialtyModel.get_by_id")
    def test_delete_specialty_fail(self, mock_specialty_get_by_id):
        mock_specialty_get_by_id.return_value = None
        wrong_specialty_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.delete(f"/specialties/{wrong_specialty_id}")
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(SPECIALTY, wrong_specialty_id),
        )
