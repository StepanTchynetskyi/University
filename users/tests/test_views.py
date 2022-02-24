from copy import deepcopy
import json
import uuid
import unittest
from unittest.mock import patch
from marshmallow import ValidationError

from users import models as user_models
from positions import models as position_models
from subjects import models as subject_models
from specialties import models as specialty_models
from groups import models as group_models
from utils.constants import (
    ALREADY_EXISTS,
    STUDENT,
    PW_DO_NOT_MATCH,
    POSITION,
    DOES_NOT_EXIST,
    NOT_FOUND_BY_ID,
    NOT_ACTIVE_USER,
    PERMISSION_DENIED,
    SUCCESSFULLY_DELETED,
    TEACHER,
    SUBJECT,
)
from utils.custom_exceptions import (
    CreateException,
    SearchException,
)
from utils.test_utils import BaseTestCase, create_obj, get_headers


class StudentTestCase(BaseTestCase):
    data = {
        "email": "stadfw1232112212fw@gmail.com",
        "first_name": "stud",
        "last_name": "student1",
        "password": "Awnafjfawga12@",
        "age": 18,
        "year_of_study": 2,
    }
    student_id, student = create_obj(data, user_models.StudentModel)
    student.is_active = True

    @patch("users.models.StudentModel.save_to_db")
    @patch("users.models.UserModel.get_by_email")
    def test_create_student_success(self, mock_get_by_email, mock_save_to_db):
        self.data["password1"] = "Awnafjfawga12@"
        mock_get_by_email.return_value = []
        mock_save_to_db.return_value = self.student
        response = self.client.post("/users/students/create", json=self.data)
        data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["age"], self.data["age"])
        self.assertEqual(data["email"], self.data["email"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["last_name"], self.data["last_name"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["type"], "student")
        self.assertEqual(data["year_of_study"], self.data["year_of_study"])

    @patch("users.models.UserModel.get_by_email")
    def test_create_student_fail_user_already_exists(self, mock_get_by_email):
        mock_get_by_email.return_value = self.student
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/students/create", json=self.data)
        self.assertEqual(
            str(context.exception),
            ALREADY_EXISTS.format(STUDENT, self.student.email),
        )

    @patch("users.models.UserModel.get_by_email")
    def test_create_student_fail_user_wrong_password(self, mock_get_by_email):
        mock_get_by_email.return_value = None
        data = deepcopy(self.data)
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/students/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)
        data["password1"] = "Awnafjfawga12@3"
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/students/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)

    def test_create_student_fail_user_missing_required_field(self):
        data = deepcopy(self.data)
        data.pop("email")
        with self.assertRaises(ValidationError) as context:
            self.client.post("/users/students/create", json=data)
        exception_message = "{'email': ['Missing data for required field.']}"
        self.assertEqual(str(context.exception), exception_message)

    def test_get_students(self):
        response = self.client.get("/users/students")
        self.assertEqual(response.status_code, 200)

    @patch("users.models.UserModel.get_by_id")
    def test_get_student_success(self, mock_student_get_by_id):
        mock_student_get_by_id.return_value = self.student
        response = self.client.get(f"users/students/{self.student_id}")
        data = json.loads(response.data.decode("utf-8"))["data"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["age"], self.data["age"])
        self.assertEqual(data["email"], self.data["email"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["last_name"], self.data["last_name"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["type"], "student")
        self.assertEqual(data["year_of_study"], self.data["year_of_study"])
        self.assertEqual(data["is_active"], True)

    @patch("users.models.StudentModel.get_by_id")
    def test_get_student_fail_wrong_student_id(self, mock_student_get_by_id):
        mock_student_get_by_id.return_value = None
        wrong_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/students/{wrong_id}")
        self.assertEqual(
            str(context.exception), NOT_FOUND_BY_ID.format(STUDENT, wrong_id)
        )

    @patch("users.models.UserModel.get_by_id")
    def test_get_student_fail_wrong_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/students/{self.student_id}")
        self.student.is_active = True
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("users.models.StudentModel.save_to_db")
    @patch("users.models.UserModel.get_by_id")
    def test_update_student_success(
        self, mock_student_get_by_id, mock_student_save_to_db
    ):
        headers = get_headers(self.student.id)
        mock_student_get_by_id.return_value = self.student
        mock_student_save_to_db.return_value = None
        data = {"year_of_study": 1}
        response = self.client.put(
            f"users/students/{self.student_id}",
            headers=headers,
            json=data,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["year_of_study"], data["year_of_study"])

    @patch("users.models.UserModel.get_by_id")
    def test_update_student_fail_wrong_student_id(
        self, mock_student_get_by_id
    ):
        mock_student_get_by_id.return_value = None
        wrong_student_id = uuid.uuid4()
        headers = get_headers(self.student.id)
        data = {"year_of_study": 1}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/students/{wrong_student_id}",
                headers=headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(STUDENT, wrong_student_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_update_student_fail_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        headers = get_headers(self.student.id)
        data = {"year_of_study": 1}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/students/{self.student_id}",
                headers=headers,
                json=data,
            )
        self.student.is_active = True
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_update_student_fail_permission_error(
        self, mock_student_get_by_id
    ):
        wrong_student_id = uuid.uuid4()
        headers = get_headers(self.student_id)
        self.student.id = wrong_student_id
        self.student.is_active = True
        mock_student_get_by_id.return_value = self.student
        data = {"year_of_study": 1}
        with self.assertRaises(PermissionError) as context:
            self.client.put(
                f"users/students/{wrong_student_id}",
                headers=headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.student_id)),
        )
        self.student.id = self.student_id

    @patch("users.models.StudentModel.remove_from_db")
    @patch("users.models.UserModel.get_by_id")
    def test_delete_student_success(
        self, mock_student_get_by_id, mock_student_remove
    ):
        mock_student_get_by_id.return_value = self.student
        headers = get_headers(self.student.id)
        mock_student_remove.return_value = None
        response = self.client.delete(
            f"users/students/{self.student.id}/hard_delete",
            headers=headers,
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(STUDENT, self.student.id)
        )

    @patch("users.models.StudentModel.get_by_id")
    def test_delete_student_fail_wrong_student_id(
        self, mock_student_get_by_id
    ):
        mock_student_get_by_id.return_value = None
        wrong_student_id = uuid.uuid4()
        headers = get_headers(self.student.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/{wrong_student_id}/hard_delete",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(STUDENT, wrong_student_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_delete_student_fail_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        headers = get_headers(self.student.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/{self.student_id}/hard_delete",
                headers=headers,
            )
        self.student.is_active = True
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_delete_student_fail_permission_error(
        self, mock_student_get_by_id
    ):
        wrong_student_id = uuid.uuid4()
        headers = get_headers(self.student.id)
        self.student.id = wrong_student_id
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/students/{wrong_student_id}/hard_delete",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.student_id)),
        )
        self.student.id = self.student_id

    @patch("users.models.StudentModel.save_to_db")
    @patch("users.models.UserModel.get_by_id")
    def test_soft_delete_student_success(
        self, mock_student_get_by_id, mock_student_save_to_db
    ):
        mock_student_get_by_id.return_value = self.student
        mock_student_save_to_db.return_value = None
        headers = get_headers(self.student.id)
        response = self.client.delete(
            f"users/students/{self.student.id}", headers=headers
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(STUDENT, self.student.id)
        )

    @patch("users.models.StudentModel.get_by_id")
    def test_delete_soft_student_fail_wrong_student_id(
        self, mock_student_get_by_id
    ):
        mock_student_get_by_id.return_value = None
        wrong_student_id = uuid.uuid4()
        headers = get_headers(self.student.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/{wrong_student_id}",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(STUDENT, wrong_student_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_delete_soft_student_fail_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        headers = get_headers(self.student.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/{self.student_id}",
                headers=headers,
            )
        self.student.is_active = True
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_delete_soft_student_fail_permission_error(
        self, mock_student_get_by_id
    ):
        wrong_student_id = uuid.uuid4()
        headers = get_headers(self.student_id)
        self.student.id = wrong_student_id
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/students/{wrong_student_id}",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.student_id)),
        )
        self.student.id = self.student_id


class TeacherTestCase(BaseTestCase):
    position_id = uuid.uuid4()
    data = {
        "email": "teacher@gmail.com",
        "first_name": "teach",
        "last_name": "teacher",
        "password": "Awnafjfawga12@",
        "age": 70,
        "position_id": position_id,
    }
    teacher_id, teacher = create_obj(data, user_models.TeacherModel)
    teacher.is_active = True
    position = position_models.PositionModel()
    position.id = position_id
    position.position_name = "Professor"

    @patch("users.models.TeacherModel.save_to_db")
    @patch("positions.models.PositionModel.get_by_id")
    @patch("users.models.UserModel.get_by_email")
    def test_create_teacher_success(
        self,
        mock_get_user_by_email,
        mock_get_position_by_id,
        mock_teacher_save_to_db,
    ):
        self.data["password1"] = "Awnafjfawga12@"
        mock_get_user_by_email.return_value = None
        mock_get_position_by_id.return_value = self.position
        mock_teacher_save_to_db.return_value = None
        response = self.client.post("/users/teachers/create", json=self.data)
        data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["age"], self.data["age"])
        self.assertEqual(data["email"], self.data["email"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["last_name"], self.data["last_name"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["type"], "teacher")
        self.assertEqual(data["position_id"], str(self.data["position_id"]))

    @patch("users.models.UserModel.get_by_email")
    def test_create_teacher_fail_user_already_exists(self, mock_get_by_email):
        mock_get_by_email.return_value = self.teacher
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/teachers/create", json=self.data)
        self.assertEqual(
            str(context.exception),
            ALREADY_EXISTS.format(TEACHER, self.teacher.email),
        )

    @patch("users.models.UserModel.get_by_email")
    def test_create_teacher_fail_user_wrong_password(self, mock_get_by_email):
        mock_get_by_email.return_value = None
        data = deepcopy(self.data)
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/teachers/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)
        data["password1"] = "Awnafjfawga12@3"
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/teachers/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)

    def test_create_teacher_fail_user_missing_required_field(self):
        data = deepcopy(self.data)
        data.pop("first_name")
        with self.assertRaises(ValidationError) as context:
            self.client.post("/users/teachers/create", json=data)
        exception_message = (
            "{'first_name': ['Missing data for required field.']}"
        )
        self.assertEqual(str(context.exception), exception_message)

    @patch("positions.models.PositionModel.get_by_id")
    @patch("users.models.UserModel.get_by_email")
    def test_create_teacher_fail_wrong_position_id(
        self, mock_get_user_by_email, mock_get_position_by_id
    ):
        wrong_position_id = uuid.uuid4()
        data = deepcopy(self.data)
        data["password1"] = "Awnafjfawga12@"
        data["position_id"] = wrong_position_id
        mock_get_user_by_email.return_value = None
        mock_get_position_by_id.return_value = None
        with self.assertRaises(SearchException) as context:
            self.client.post("/users/teachers/create", json=data)
        self.assertEqual(
            str(context.exception),
            DOES_NOT_EXIST.format(POSITION, wrong_position_id),
        )

    def test_get_teachers(self):
        response = self.client.get("/users/teachers/")
        self.assertEqual(response.status_code, 200)

    @patch("users.models.UserModel.get_by_id")
    def test_get_teacher_success(self, mock_teacher_get_by_id):
        mock_teacher_get_by_id.return_value = self.teacher
        response = self.client.get(f"users/teachers/{self.teacher_id}/")
        data = json.loads(response.data.decode("utf-8"))["data"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["age"], self.data["age"])
        self.assertEqual(data["email"], self.data["email"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["last_name"], self.data["last_name"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["type"], "teacher")
        self.assertEqual(data["is_active"], True)

    @patch("users.models.TeacherModel.get_by_id")
    def test_get_teacher_fail_wrong_teacher_id(self, mock_teacher_get_by_id):
        mock_teacher_get_by_id.return_value = None
        wrong_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/teachers/{wrong_id}/")
        self.assertEqual(
            str(context.exception), NOT_FOUND_BY_ID.format(TEACHER, wrong_id)
        )

    @patch("users.models.UserModel.get_by_id")
    def test_get_teacher_fail_wrong_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/teachers/{self.teacher_id}/")
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )
        self.teacher.is_active = True

    @patch("users.models.TeacherModel.save_to_db")
    @patch("users.models.UserModel.get_by_id")
    def test_update_teacher_success(
        self, mock_teacher_get_by_id, mock_teacher_save_to_db
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_teacher_save_to_db.return_value = None
        headers = get_headers(self.teacher.id)
        data = {"first_name": "teacher2"}
        response = self.client.put(
            f"users/teachers/{self.teacher_id}/",
            headers=headers,
            json=data,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["first_name"], data["first_name"])

    @patch("users.models.TeacherModel.save_to_db")
    @patch("positions.models.PositionModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_update_teacher_success_update_position_id(
        self,
        mock_teacher_get_by_id,
        mock_position_get_by_id,
        mock_teacher_save_to_db,
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_position_get_by_id.return_value = self.position
        mock_teacher_save_to_db.return_value = None
        headers = get_headers(self.teacher.id)
        data = {"position_id": uuid.uuid4()}
        response = self.client.put(
            f"users/teachers/{self.teacher.id}/",
            headers=headers,
            json=data,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data["position_id"], str(data["position_id"])
        )

    @patch("positions.models.PositionModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_update_teacher_fail_update_position_id(
        self, mock_teacher_get_by_id, mock_position_get_by_id
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_position_get_by_id.return_value = None
        wrong_position_id = uuid.uuid4()
        headers = get_headers(self.teacher.id)
        data = {"position_id": wrong_position_id}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/teachers/{self.teacher_id}/",
                headers=headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            DOES_NOT_EXIST.format(POSITION, wrong_position_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_update_teacher_fail_wrong_teacher_id(
        self, mock_teacher_get_by_id
    ):
        mock_teacher_get_by_id.return_value = None
        wrong_teacher_id = uuid.uuid4()
        data = {"first_name": "teacher2"}
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/teachers/{wrong_teacher_id}/",
                headers=headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(TEACHER, wrong_teacher_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_update_teacher_fail_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        headers = get_headers(self.teacher.id)
        data = {"first_name": "teacher2"}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/teachers/{self.teacher_id}/",
                headers=headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )
        self.teacher.is_active = True

    @patch("users.models.UserModel.get_by_id")
    def test_update_teacher_fail_permission_error(
        self, mock_teacher_get_by_id
    ):
        wrong_teacher_id = uuid.uuid4()
        headers = get_headers(self.teacher_id)
        self.teacher.id = wrong_teacher_id
        self.teacher.is_active = True
        mock_teacher_get_by_id.return_value = self.teacher
        data = {"first_name": "teacher2"}
        with self.assertRaises(PermissionError) as context:
            self.client.put(
                f"users/teachers/{wrong_teacher_id}/",
                headers=headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.teacher_id)),
        )
        self.teacher.id = self.teacher_id

    @patch("users.models.TeacherModel.remove_from_db")
    @patch("users.models.UserModel.get_by_id")
    def test_delete_teacher_success(
        self, mock_teacher_get_by_id, mock_teacher_remove
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_teacher_remove.return_value = None
        headers = get_headers(self.teacher.id)
        response = self.client.delete(
            f"users/teachers/{self.teacher.id}/hard_delete",
            headers=headers,
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(TEACHER, self.teacher.id)
        )

    @patch("users.models.TeacherModel.get_by_id")
    def test_delete_student_fail_wrong_student_id(
        self, mock_teacher_get_by_id
    ):
        mock_teacher_get_by_id.return_value = None
        wrong_teacher_id = uuid.uuid4()
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/{wrong_teacher_id}/hard_delete",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(TEACHER, wrong_teacher_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_delete_teacher_fail_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/{self.teacher_id}/hard_delete",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )
        self.teacher.is_active = True

    @patch("users.models.UserModel.get_by_id")
    def test_delete_teacher_fail_permission_error(
        self, mock_teacher_get_by_id
    ):
        wrong_teacher_id = uuid.uuid4()
        headers = get_headers(self.teacher_id)
        self.teacher.id = wrong_teacher_id
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/teachers/{wrong_teacher_id}/hard_delete",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.teacher_id)),
        )
        self.teacher.id = self.teacher_id

    @patch("users.models.TeacherModel.save_to_db")
    @patch("users.models.UserModel.get_by_id")
    def test_soft_delete_teacher_success(
        self, mock_teacher_get_by_id, mock_teacher_save_to_db
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_teacher_save_to_db.return_value = None
        headers = get_headers(self.teacher.id)
        response = self.client.delete(
            f"users/teachers/{self.teacher.id}/", headers=headers
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(TEACHER, self.teacher.id)
        )

    @patch("users.models.TeacherModel.get_by_id")
    def test_delete_soft_teacher_fail_wrong_teacher_id(
        self, mock_teacher_get_by_id
    ):
        mock_teacher_get_by_id.return_value = None
        wrong_teacher_id = uuid.uuid4()
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/{wrong_teacher_id}/",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(TEACHER, wrong_teacher_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_delete_soft_teacher_fail_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/{self.teacher_id}/",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )
        self.teacher.is_active = True

    @patch("users.models.UserModel.get_by_id")
    def test_delete_soft_teacher_fail_permission_error(
        self, mock_teacher_get_by_id
    ):
        wrong_teacher_id = uuid.uuid4()
        headers = get_headers(self.teacher.id)
        self.teacher.id = wrong_teacher_id
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/teachers/{wrong_teacher_id}/",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.teacher_id)),
        )
        self.teacher.id = self.teacher_id


class AppointItemsTestCase(BaseTestCase):
    data_teacher = {
        "email": "teacher@gmail.com",
        "first_name": "teach",
        "last_name": "teacher",
        "password": "Awnafjfawga12@",
        "age": 70,
        "is_active": True,
    }
    data_student = {
        "email": "teacher@gmail.com",
        "first_name": "teach",
        "last_name": "teacher",
        "password": "Awnafjfawga12@",
        "age": 70,
        "year_of_study": 1,
    }
    data_subject1 = {"name": "English", "year": 2020, "credits": 2}
    data_subject2 = {"name": "Math", "year": 2021, "credits": 4}
    subject1_id, subject1 = create_obj(
        data_subject1, subject_models.SubjectModel
    )
    subject2_id, subject2 = create_obj(
        data_subject2, subject_models.SubjectModel
    )
    teacher_id, teacher = create_obj(data_teacher, user_models.TeacherModel)
    student_id, student = create_obj(data_student, user_models.StudentModel)
    data_specialty = {"name": "IKNI", "year": 2021, "teacher_id": teacher_id}
    specialty_id, specialty = create_obj(
        data_specialty, specialty_models.SpecialtyModel
    )
    data_group = {
        "name": "SA-42",
        "year": 2021,
        "credits_per_student": 35,
        "curator_id": teacher_id,
        "specialty_id": specialty_id,
    }
    group_id, group = create_obj(data_group, group_models.GroupModel)
    teacher.is_active = True

    @patch("users.models.TeacherModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_appoint_subject_to_teacher_success(
        self,
        mock_teacher_get_by_id,
        mock_subject_get_by_id,
        mock_teacher_save_to_db,
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_subject_get_by_id.return_value = self.subject1
        mock_teacher_save_to_db.return_value = None
        headers = get_headers(self.teacher.id)
        response = self.client.post(
            f"users/teachers/{self.teacher_id}/appoint-subjects/{self.subject1_id}",
            headers=headers,
        )
        data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["subjects"][0]["id"], str(self.subject1_id))
        self.assertEqual(data["subjects"][0]["name"], self.subject1.name)
        self.assertEqual(data["id"], str(self.teacher.id))

    @patch("users.models.TeacherModel.get_by_id")
    def test_test_appoint_subject_to_teacher_fail_teacher_not_found(
        self, mock_teacher_get_by_id
    ):
        mock_teacher_get_by_id.return_value = None
        wrong_teacher_id = uuid.uuid4()
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.post(
                f"users/teachers/{wrong_teacher_id}/appoint-subjects/{self.subject1_id}",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(TEACHER, wrong_teacher_id),
        )

    @patch("users.models.UserModel.get_by_id")
    def test_test_appoint_subject_to_teacher_fail_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.post(
                f"users/teachers/{self.teacher_id}/appoint-subjects/{self.subject1_id}",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )
        self.teacher.is_active = True

    @patch("subjects.models.SubjectModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_appoint_subject_to_teacher_fail_subject_not_found(
        self, mock_teacher_get_by_id, mock_subject_get_by_id
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_subject_get_by_id.return_value = None
        wrong_subject_id = uuid.uuid4()
        headers = get_headers(self.teacher.id)
        with self.assertRaises(SearchException) as context:
            self.client.post(
                f"users/teachers/{self.teacher_id}/appoint-subjects/{wrong_subject_id}",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(SUBJECT, wrong_subject_id),
        )

    @patch("users.models.TeacherModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_ids")
    @patch("users.models.UserModel.get_by_id")
    def test_appoint_subjects_to_teacher_success(
        self,
        mock_teacher_get_by_id,
        mock_subject_get_by_ids,
        mock_teacher_save_to_db,
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_subject_get_by_ids.return_value = [self.subject1, self.subject2]
        initial_subjects_len = len(self.teacher.subjects)
        data = {"subject_ids": [self.subject1_id, self.subject2_id]}
        mock_teacher_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.post(
            f"users/teachers/{self.teacher_id}/appoint-subjects-to-teacher",
            json=data,
            headers=headers,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response_data["subjects"]) - initial_subjects_len,
            len(data["subject_ids"]),
        )

    @patch("groups.models.GroupModel.save_to_db")
    @patch("users.models.StudentModel.get_by_ids")
    @patch("groups.models.GroupModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_appoint_student_to_group(
        self,
        mock_teacher_get_by_id,
        mock_group_get_by_id,
        mock_student_get_by_ids,
        mock_group_save_to_db,
    ):
        data = {"student_ids": [self.student_id]}
        mock_teacher_get_by_id.return_value = self.teacher
        mock_group_get_by_id.return_value = self.group
        mock_student_get_by_ids.return_value = [self.student]
        mock_group_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.post(
            f"users/teachers/{self.teacher_id}/appoint-student-to-group/groups/{self.group_id}",
            json=data,
            headers=headers,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], str(self.group_id))
        self.assertEqual(response_data["curator_id"], str(self.teacher_id))

    @patch("specialties.models.SpecialtyModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_ids")
    @patch("specialties.models.SpecialtyModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_appoint_subject_to_specialty(
        self,
        mock_teacher_get_by_id,
        mock_specialty_get_by_id,
        mock_subject_get_by_ids,
        mock_specialty_save_to_db,
    ):
        data = {"subject_ids": [self.subject1_id, self.subject2_id]}
        mock_teacher_get_by_id.return_value = self.teacher
        mock_specialty_get_by_id.return_value = self.specialty
        mock_subject_get_by_ids.return_value = [self.subject1, self.subject2]
        mock_specialty_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.post(
            f"users/teachers/{self.teacher_id}/appoint-subjects-to-specialty/specialties/{self.specialty_id}",
            json=data,
            headers=headers,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], str(self.specialty_id))

    @patch("groups.models.GroupModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_ids")
    @patch("groups.models.GroupModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_appoint_subject_to_group(
        self,
        mock_teacher_get_by_id,
        mock_group_get_by_id,
        mock_subject_get_by_ids,
        mock_group_save_to_db,
    ):
        data = {"subject_ids": [self.subject1_id, self.subject2_id]}
        mock_teacher_get_by_id.return_value = self.teacher
        mock_group_get_by_id.return_value = self.group
        mock_subject_get_by_ids.return_value = [self.subject1, self.subject2]
        mock_group_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.post(
            f"users/teachers/{self.teacher_id}/appoint-subject-to-group/groups/{self.group_id}",
            json=data,
            headers=headers,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], str(self.group_id))

    @patch("users.models.TeacherModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_remove_subject_from_teacher_success(
        self,
        mock_teacher_get_by_id,
        mock_subject_get_by_id,
        mock_teacher_save_to_db,
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        self.teacher.subjects = [self.subject1]
        mock_subject_get_by_id.return_value = self.subject1
        mock_teacher_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.delete(
            f"users/teachers/{self.teacher_id}/disappoint-subject/subjects/{self.subject1_id}",
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response_data["id"], str(self.teacher_id))
        self.assertListEqual(response_data["subjects"], [])

    @patch("subjects.models.SubjectModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_remove_subject_from_teacher_fail(
        self, mock_teacher_get_by_id, mock_subject_get_by_id
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        self.teacher.subjects = [self.subject1]
        mock_subject_get_by_id.return_value = None
        wrong_subject_id = uuid.uuid4()
        headers = get_headers(self.teacher_id)
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/{self.teacher_id}/disappoint-subject/subjects/{wrong_subject_id}",
                headers=headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(SUBJECT, wrong_subject_id),
        )

    @patch("users.models.TeacherModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_ids")
    @patch("users.models.UserModel.get_by_id")
    def test_remove_subjects_from_teacher(
        self,
        mock_teacher_get_by_id,
        mock_subject_get_by_ids,
        mock_teacher_save_to_db,
    ):
        data = {"subject_ids": [self.subject1_id]}
        mock_teacher_get_by_id.return_value = self.teacher
        self.teacher.subjects = [self.subject1]
        mock_subject_get_by_ids.return_value = [self.subject1]
        mock_teacher_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.delete(
            f"users/teachers/{self.teacher_id}/disappoint-subjects-from-teacher",
            json=data,
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response_data["id"], str(self.teacher_id))
        self.assertListEqual(response_data["subjects"], [])

    @patch("groups.models.GroupModel.save_to_db")
    @patch("users.models.StudentModel.get_by_ids")
    @patch("groups.models.GroupModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_remove_student_from_group(
        self,
        mock_teacher_get_by_id,
        mock_group_get_by_id,
        mock_student_get_by_ids,
        mock_group_save_to_db,
    ):
        data = {"student_ids": [self.student_id]}
        mock_teacher_get_by_id.return_value = self.teacher
        mock_group_get_by_id.return_value = self.group
        self.group.students = [self.student]
        mock_student_get_by_ids.return_value = [self.student]
        mock_group_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.delete(
            f"users/teachers/{self.teacher_id}/disappoint-student-from-group/groups/{self.group_id}",
            json=data,
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response_data["id"], str(self.group_id))
        self.assertListEqual(response_data["students"], [])

    @patch("specialties.models.SpecialtyModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_ids")
    @patch("specialties.models.SpecialtyModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_remove_subject_from_specialty(
        self,
        mock_teacher_get_by_id,
        mock_specialty_get_by_id,
        mock_subject_get_by_ids,
        mock_specialty_save_to_db,
    ):
        data = {"subject_ids": [self.subject1_id]}
        mock_teacher_get_by_id.return_value = self.teacher
        mock_specialty_get_by_id.return_value = self.specialty
        self.specialty.subjects = [self.subject1]
        mock_subject_get_by_ids.return_value = [self.subject1]
        mock_specialty_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.delete(
            f"users/teachers/{self.teacher_id}/disappoint-subjects-from-specialty/"
            f"specialties/{self.specialty_id}",
            json=data,
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response_data["id"], str(self.specialty_id))
        self.assertListEqual(response_data["subjects"], [])

    @patch("groups.models.GroupModel.save_to_db")
    @patch("subjects.models.SubjectModel.get_by_ids")
    @patch("groups.models.GroupModel.get_by_id")
    @patch("users.models.UserModel.get_by_id")
    def test_remove_subject_from_group(
        self,
        mock_teacher_get_by_id,
        mock_group_get_by_id,
        mock_subject_get_by_ids,
        mock_group_save_to_db,
    ):
        data = {"subject_ids": [self.subject1_id]}
        mock_teacher_get_by_id.return_value = self.teacher
        mock_group_get_by_id.return_value = self.group
        self.group.subjects = [self.subject1]
        mock_subject_get_by_ids.return_value = [self.subject1]
        mock_group_save_to_db.return_value = None
        headers = get_headers(self.teacher_id)
        response = self.client.delete(
            f"users/teachers/{self.teacher_id}/disappoint-subjects-from-group/groups/{self.group_id}",
            json=data,
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response_data["id"], str(self.group_id))
        self.assertListEqual(response_data["subjects"], [])


if __name__ == "__main__":
    unittest.main()
