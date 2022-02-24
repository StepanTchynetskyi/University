import json
import uuid

import unittest
from unittest.mock import patch

from utils import test_utils
from users import models as user_models
from positions import models as position_models
from subjects import models as subject_models
from utils.constants import (
    NOT_FOUND_BY_ID,
    SUBJECT,
    ITEM_NOT_FOUND_IN_ARRAY,
    TEACHER,
)
from utils.custom_exceptions import SearchException


class SubjectTestCase(test_utils.BaseTestCase):
    position_id = uuid.uuid4()
    data = {
        "email": "teacher@gmail.com",
        "first_name": "teach",
        "last_name": "teacher",
        "password": "Awnafjfawga12@",
        "age": 70,
        "is_active": True,
        "position_id": position_id,
    }
    teacher_id, teacher = test_utils.create_obj(data, user_models.TeacherModel)
    position = position_models.PositionModel()
    position.id = position_id
    position.position_name = "Professor"
    data_subject1 = {"name": "English", "year": 2020, "credits": 2}
    subject1_id, subject1 = test_utils.create_obj(
        data_subject1, subject_models.SubjectModel
    )

    @patch("users.models.TeacherModel.save_to_db")
    @patch("subjects.models.SubjectModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_name_and_year")
    @patch("users.models.UserModel.get_by_id")
    def test_create_subject(
        self,
        mock_teacher_get_by_id,
        mock_subject_get_by_name_and_year,
        mock_subject_save_to_db,
        mock_teacher_save_to_db,
    ):

        mock_teacher_get_by_id.return_value = self.teacher
        mock_subject_get_by_name_and_year.return_value = None
        mock_subject_save_to_db.return_value = None
        mock_teacher_save_to_db.return_value = None
        headers = test_utils.get_headers(self.teacher_id)
        response = self.client.post(
            f"/users/teachers/{self.teacher_id}/subjects/create",
            json=self.data_subject1,
            headers=headers,
        )
        self.assertEqual(response.status_code, 201)

    @patch("subjects.models.SubjectModel.get_all_records")
    def test_get_subjects(self, mock_subject_get_all_records):
        mock_subject_get_all_records.return_value = [self.subject1]
        response = self.client.get("/subjects")
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data["subjects"][0]["id"], str(self.subject1_id)
        )

    @patch("subjects.models.SubjectModel.get_by_id")
    def test_get_subject_success(self, mock_subject_get_by_id):
        mock_subject_get_by_id.return_value = self.subject1
        response = self.client.get(f"/subjects/{self.subject1_id}")
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], str(self.subject1_id))

    @patch("subjects.models.SubjectModel.get_by_id")
    def test_get_subject_fail(self, mock_subject_get_by_id):
        mock_subject_get_by_id.return_value = None
        wrong_subject_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.get(f"/subjects/{wrong_subject_id}")
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(SUBJECT, wrong_subject_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_get_teacher_subjects(self, mock_teacher_get_by_id):
        mock_teacher_get_by_id.return_value = self.teacher
        self.teacher.subjects = [self.subject1]
        response = self.client.get(
            f"users/teachers/{self.teacher_id}/subjects"
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data["subjects"][0]["id"], str(self.subject1_id)
        )

    @patch("users.models.UserModel.get_by_id")
    def test_get_teacher_subject_success(self, mock_teacher_get_by_id):
        mock_teacher_get_by_id.return_value = self.teacher
        self.teacher.subjects = [self.subject1]
        response = self.client.get(
            f"users/teachers/{self.teacher_id}/subjects/{self.subject1_id}"
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], str(self.subject1_id))

    @patch("users.models.UserModel.get_by_id")
    def test_get_teacher_subject_fail(self, mock_teacher_get_by_id):
        mock_teacher_get_by_id.return_value = self.teacher
        wrong_subject_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.get(
                f"users/teachers/{self.teacher_id}/subjects/{wrong_subject_id}"
            )
        self.assertEqual(
            str(context.exception),
            ITEM_NOT_FOUND_IN_ARRAY.format(
                SUBJECT, wrong_subject_id, TEACHER, self.teacher_id
            ),
        )

    @patch("subjects.models.SubjectModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_name_and_year")
    @patch("users.models.UserModel.get_by_id")
    def test_update_subject(
        self,
        mock_teacher_get_by_id,
        mock_subject_get_by_name_and_year,
        mock_subject_save_to_db,
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        self.teacher.subjects = [self.subject1]
        mock_subject_get_by_name_and_year.return_value = None
        mock_subject_save_to_db.return_value = None
        headers = test_utils.get_headers(self.teacher_id)
        data = {"year": 2022}
        response = self.client.put(
            f"users/teachers/{self.teacher_id}/subjects/{self.subject1_id}",
            json=data,
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)

    @patch("subjects.models.SubjectModel.remove_from_db")
    @patch("users.models.UserModel.get_by_id")
    def test_delete_subject(
        self, mock_teacher_get_by_id, mock_subject_remove_from_db
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_subject_remove_from_db.return_value = None
        self.teacher.subjects = [self.subject1]
        headers = test_utils.get_headers(self.teacher_id)
        response = self.client.delete(
            f"users/teachers/{self.teacher_id}/subjects/{self.subject1_id}",
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
