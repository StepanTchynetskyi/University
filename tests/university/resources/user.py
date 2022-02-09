from copy import deepcopy
import json
import uuid
import unittest
from unittest.mock import patch

from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError

from application import create_app, PositionModel
from application.university.models.user import StudentModel, TeacherModel

from application.university.utils.constants import (
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
)
from application.university.utils.custom_exceptions import (
    CreateException,
    SearchException,
)


def _setUp(obj, user):
    obj.app = create_app()
    obj.ctx = obj.app.app_context()
    obj.ctx.push()
    obj.client = obj.app.test_client()
    obj.access_token = create_access_token(identity=user.id, fresh=True)
    obj.headers = {"Authorization": "Bearer {}".format(obj.access_token)}
    user.is_active = True


def create_user_obj(data, model):
    obj_id = uuid.uuid4()
    obj = model()
    obj.id = obj_id
    for key, value in data.items():
        setattr(obj, key, value)
    return obj_id, obj


class StudentTestCase(unittest.TestCase):
    data = {
        "email": "stadfw1232112212fw@gmail.com",
        "first_name": "stud",
        "last_name": "student1",
        "password": "Awnafjfawga12@",
        "age": 18,
        "year_of_study": 2,
    }
    student_id, student = create_user_obj(data, StudentModel)

    def setUp(self) -> None:
        _setUp(self, self.student)

    def tearDown(self) -> None:
        self.ctx.pop()

    @patch("application.university.models.user.StudentModel.save_to_db")
    @patch("application.university.models.user.UserModel.get_by_email")
    def test_create_student_success(self, mock_get_by_email, mock_save_to_db):
        self.data["password1"] = "Awnafjfawga12@"
        mock_get_by_email.return_value = []
        mock_save_to_db.return_value = self.student
        response = self.client.post(
            "/users/students/student/create", json=self.data
        )
        data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["age"], self.data["age"])
        self.assertEqual(data["email"], self.data["email"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["last_name"], self.data["last_name"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["type"], "student")
        self.assertEqual(data["year_of_study"], self.data["year_of_study"])

    @patch("application.university.models.user.UserModel.get_by_email")
    def test_create_student_fail_user_already_exists(self, mock_get_by_email):
        mock_get_by_email.return_value = self.student
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/students/student/create", json=self.data)
        self.assertEqual(
            str(context.exception),
            ALREADY_EXISTS.format(STUDENT, self.student.email),
        )

    @patch("application.university.models.user.UserModel.get_by_email")
    def test_create_student_fail_user_wrong_password(self, mock_get_by_email):
        mock_get_by_email.return_value = None
        data = deepcopy(self.data)
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/students/student/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)
        data["password1"] = "Awnafjfawga12@3"
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/students/student/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)

    def test_create_student_fail_user_missing_required_field(self):
        data = deepcopy(self.data)
        data.pop("email")
        with self.assertRaises(ValidationError) as context:
            self.client.post("/users/students/student/create", json=data)
        exception_message = "{'email': ['Missing data for required field.']}"
        self.assertEqual(str(context.exception), exception_message)

    def test_get_students(self):
        response = self.client.get("/users/students")
        self.assertEqual(response.status_code, 200)

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_get_student_success(self, mock_student_get_by_id):
        mock_student_get_by_id.return_value = self.student
        response = self.client.get(f"users/students/student/{self.student_id}")
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

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_get_student_fail_wrong_student_id(self, mock_student_get_by_id):
        mock_student_get_by_id.return_value = None
        wrong_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/students/student/{wrong_id}")
        self.assertEqual(
            str(context.exception), NOT_FOUND_BY_ID.format(STUDENT, wrong_id)
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_get_student_fail_wrong_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/students/student/{self.student_id}")
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("application.university.models.user.StudentModel.save_to_db")
    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_update_student_success(
        self, mock_student_get_by_id, mock_student_save_to_db
    ):
        mock_student_get_by_id.return_value = self.student
        mock_student_save_to_db.return_value = None
        data = {"year_of_study": 1}
        response = self.client.put(
            f"users/students/student/{self.student_id}",
            headers=self.headers,
            json=data,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["year_of_study"], data["year_of_study"])

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_update_student_fail_wrong_student_id(
        self, mock_student_get_by_id
    ):
        mock_student_get_by_id.return_value = None
        wrong_student_id = uuid.uuid4()
        data = {"year_of_study": 1}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/students/student/{wrong_student_id}",
                headers=self.headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(STUDENT, wrong_student_id),
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_update_student_fail_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        data = {"year_of_study": 1}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/students/student/{self.student_id}",
                headers=self.headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_update_student_fail_permission_error(
        self, mock_student_get_by_id
    ):
        wrong_student_id = uuid.uuid4()
        self.student.id = wrong_student_id
        mock_student_get_by_id.return_value = self.student
        data = {"year_of_study": 1}
        with self.assertRaises(PermissionError) as context:
            self.client.put(
                f"users/students/student/{wrong_student_id}",
                headers=self.headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.student_id)),
        )
        self.student.id = self.student_id

    @patch("application.university.models.user.StudentModel.remove_from_db")
    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_delete_student_success(
        self, mock_student_get_by_id, mock_student_remove
    ):
        mock_student_get_by_id.return_value = self.student
        mock_student_remove.return_value = None
        response = self.client.delete(
            f"users/students/student/hard_delete/{self.student_id}",
            headers=self.headers,
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(STUDENT, self.student_id)
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_delete_student_fail_wrong_student_id(
        self, mock_student_get_by_id
    ):
        mock_student_get_by_id.return_value = None
        wrong_student_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/student/hard_delete/{wrong_student_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(STUDENT, wrong_student_id),
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_delete_student_fail_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/student/hard_delete/{self.student_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_delete_student_fail_permission_error(
        self, mock_student_get_by_id
    ):
        wrong_student_id = uuid.uuid4()
        self.student.id = wrong_student_id
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/students/student/hard_delete/{wrong_student_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.student_id)),
        )
        self.student.id = self.student_id

    @patch("application.university.models.user.StudentModel.save_to_db")
    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_soft_delete_student_success(
        self, mock_student_get_by_id, mock_student_save_to_db
    ):
        mock_student_get_by_id.return_value = self.student
        mock_student_save_to_db.return_value = None
        response = self.client.delete(
            f"users/students/student/{self.student_id}", headers=self.headers
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(STUDENT, self.student_id)
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_delete_soft_student_fail_wrong_student_id(
        self, mock_student_get_by_id
    ):
        mock_student_get_by_id.return_value = None
        wrong_student_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/student/{wrong_student_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(STUDENT, wrong_student_id),
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_delete_soft_student_fail_student_not_active(
        self, mock_student_get_by_id
    ):
        self.student.is_active = False
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/students/student/{self.student_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(STUDENT, self.student_id),
        )

    @patch("application.university.models.user.StudentModel.get_by_id")
    def test_delete_soft_student_fail_permission_error(
        self, mock_student_get_by_id
    ):
        wrong_student_id = uuid.uuid4()
        self.student.id = wrong_student_id
        mock_student_get_by_id.return_value = self.student
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/students/student/{wrong_student_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.student_id)),
        )
        self.student.id = self.student_id


class TeacherTestCase(unittest.TestCase):
    position_id = uuid.uuid4()
    data = {
        "email": "teacher@gmail.com",
        "first_name": "teach",
        "last_name": "teacher",
        "password": "Awnafjfawga12@",
        "age": 70,
        "position_id": position_id,
    }
    teacher_id, teacher = create_user_obj(data, TeacherModel)

    position = PositionModel()
    position.id = position_id
    position.position_name = "Professor"

    def setUp(self) -> None:
        _setUp(self, self.teacher)

    def tearDown(self) -> None:
        self.ctx.pop()

    @patch("application.university.models.user.TeacherModel.save_to_db")
    @patch("application.university.models.position.PositionModel.get_by_id")
    @patch("application.university.models.user.UserModel.get_by_email")
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
        response = self.client.post(
            "/users/teachers/teacher/create", json=self.data
        )
        data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["age"], self.data["age"])
        self.assertEqual(data["email"], self.data["email"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["last_name"], self.data["last_name"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["type"], "teacher")
        self.assertEqual(data["position_id"], str(self.data["position_id"]))

    @patch("application.university.models.user.UserModel.get_by_email")
    def test_create_teacher_fail_user_already_exists(self, mock_get_by_email):
        mock_get_by_email.return_value = self.teacher
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/teachers/teacher/create", json=self.data)
        self.assertEqual(
            str(context.exception),
            ALREADY_EXISTS.format(TEACHER, self.teacher.email),
        )

    @patch("application.university.models.user.UserModel.get_by_email")
    def test_create_teacher_fail_user_wrong_password(self, mock_get_by_email):
        mock_get_by_email.return_value = None
        data = deepcopy(self.data)
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/teachers/teacher/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)
        data["password1"] = "Awnafjfawga12@3"
        with self.assertRaises(CreateException) as context:
            self.client.post("/users/teachers/teacher/create", json=data)
        self.assertEqual(str(context.exception), PW_DO_NOT_MATCH)

    def test_create_teacher_fail_user_missing_required_field(self):
        data = deepcopy(self.data)
        data.pop("first_name")
        with self.assertRaises(ValidationError) as context:
            self.client.post("/users/teachers/teacher/create", json=data)
        exception_message = (
            "{'first_name': ['Missing data for required field.']}"
        )
        self.assertEqual(str(context.exception), exception_message)

    @patch("application.university.models.position.PositionModel.get_by_id")
    @patch("application.university.models.user.UserModel.get_by_email")
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
            self.client.post("/users/teachers/teacher/create", json=data)
        self.assertEqual(
            str(context.exception),
            DOES_NOT_EXIST.format(POSITION, wrong_position_id),
        )

    def test_get_teachers(self):
        response = self.client.get("/users/teachers")
        self.assertEqual(response.status_code, 200)

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_get_teacher_success(self, mock_teacher_get_by_id):
        mock_teacher_get_by_id.return_value = self.teacher
        response = self.client.get(f"users/teachers/teacher/{self.teacher_id}")
        data = json.loads(response.data.decode("utf-8"))["data"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["age"], self.data["age"])
        self.assertEqual(data["email"], self.data["email"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["last_name"], self.data["last_name"])
        self.assertEqual(data["first_name"], self.data["first_name"])
        self.assertEqual(data["type"], "teacher")
        self.assertEqual(data["is_active"], True)

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_get_teacher_fail_wrong_teacher_id(self, mock_teacher_get_by_id):
        mock_teacher_get_by_id.return_value = None
        wrong_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/teachers/teacher/{wrong_id}")
        self.assertEqual(
            str(context.exception), NOT_FOUND_BY_ID.format(TEACHER, wrong_id)
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_get_teacher_fail_wrong_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(SearchException) as context:
            self.client.get(f"users/teachers/teacher/{self.teacher_id}")
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )

    @patch("application.university.models.user.TeacherModel.save_to_db")
    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_update_teacher_success(
        self, mock_teacher_get_by_id, mock_teacher_save_to_db
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_teacher_save_to_db.return_value = None
        data = {"first_name": "teacher2"}
        response = self.client.put(
            f"users/teachers/teacher/{self.teacher_id}",
            headers=self.headers,
            json=data,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["first_name"], data["first_name"])

    @patch("application.university.models.user.TeacherModel.save_to_db")
    @patch("application.university.models.position.PositionModel.get_by_id")
    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_update_teacher_success_update_position_id(
        self,
        mock_teacher_get_by_id,
        mock_position_get_by_id,
        mock_teacher_save_to_db,
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_position_get_by_id.return_value = self.position
        mock_teacher_save_to_db.return_value = None
        data = {"position_id": uuid.uuid4()}
        response = self.client.put(
            f"users/teachers/teacher/{self.teacher_id}",
            headers=self.headers,
            json=data,
        )
        response_data = json.loads(response.data.decode("utf-8"))["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_data["position_id"], str(data["position_id"])
        )

    @patch("application.university.models.position.PositionModel.get_by_id")
    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_update_teacher_fail_update_position_id(
        self, mock_teacher_get_by_id, mock_position_get_by_id
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_position_get_by_id.return_value = None
        wrong_position_id = uuid.uuid4()
        data = {"position_id": wrong_position_id}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/teachers/teacher/{self.teacher_id}",
                headers=self.headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            DOES_NOT_EXIST.format(POSITION, wrong_position_id),
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_update_teacher_fail_wrong_teacher_id(
        self, mock_teacher_get_by_id
    ):
        mock_teacher_get_by_id.return_value = None
        wrong_teacher_id = uuid.uuid4()
        data = {"first_name": "teacher2"}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/teachers/teacher/{wrong_teacher_id}",
                headers=self.headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(TEACHER, wrong_teacher_id),
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_update_teacher_fail_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        data = {"first_name": "teacher2"}
        with self.assertRaises(SearchException) as context:
            self.client.put(
                f"users/teachers/teacher/{self.teacher_id}",
                headers=self.headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_update_teacher_fail_permission_error(
        self, mock_teacher_get_by_id
    ):
        wrong_teacher_id = uuid.uuid4()
        self.teacher.id = wrong_teacher_id
        mock_teacher_get_by_id.return_value = self.teacher
        data = {"first_name": "teacher2"}
        with self.assertRaises(PermissionError) as context:
            self.client.put(
                f"users/teachers/teacher/{wrong_teacher_id}",
                headers=self.headers,
                json=data,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.teacher_id)),
        )
        self.teacher.id = self.teacher_id

    @patch("application.university.models.user.TeacherModel.remove_from_db")
    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_delete_teacher_success(
        self, mock_teacher_get_by_id, mock_teacher_remove
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_teacher_remove.return_value = None
        response = self.client.delete(
            f"users/teachers/teacher/hard_delete/{self.teacher_id}",
            headers=self.headers,
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(TEACHER, self.teacher_id)
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_delete_student_fail_wrong_student_id(
        self, mock_teacher_get_by_id
    ):
        mock_teacher_get_by_id.return_value = None
        wrong_teacher_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/teacher/hard_delete/{wrong_teacher_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(TEACHER, wrong_teacher_id),
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_delete_teacher_fail_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/teacher/hard_delete/{self.teacher_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_delete_teacher_fail_permission_error(
        self, mock_teacher_get_by_id
    ):
        wrong_teacher_id = uuid.uuid4()
        self.teacher.id = wrong_teacher_id
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/teachers/teacher/hard_delete/{wrong_teacher_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.teacher_id)),
        )
        self.teacher.id = self.teacher_id

    @patch("application.university.models.user.TeacherModel.save_to_db")
    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_soft_delete_teacher_success(
        self, mock_teacher_get_by_id, mock_teacher_save_to_db
    ):
        mock_teacher_get_by_id.return_value = self.teacher
        mock_teacher_save_to_db.return_value = None
        response = self.client.delete(
            f"users/teachers/teacher/{self.teacher_id}", headers=self.headers
        )
        message = json.loads(response.data.decode("utf-8"))["message"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            message, SUCCESSFULLY_DELETED.format(TEACHER, self.teacher_id)
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_delete_soft_teacher_fail_wrong_teacher_id(
        self, mock_teacher_get_by_id
    ):
        mock_teacher_get_by_id.return_value = None
        wrong_teacher_id = uuid.uuid4()
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/teacher/{wrong_teacher_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_FOUND_BY_ID.format(TEACHER, wrong_teacher_id),
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_delete_soft_teacher_fail_teacher_not_active(
        self, mock_teacher_get_by_id
    ):
        self.teacher.is_active = False
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(SearchException) as context:
            self.client.delete(
                f"users/teachers/teacher/{self.teacher_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            NOT_ACTIVE_USER.format(TEACHER, self.teacher_id),
        )

    @patch("application.university.models.user.TeacherModel.get_by_id")
    def test_delete_soft_teacher_fail_permission_error(
        self, mock_teacher_get_by_id
    ):
        wrong_teacher_id = uuid.uuid4()
        self.teacher.id = wrong_teacher_id
        mock_teacher_get_by_id.return_value = self.teacher
        with self.assertRaises(PermissionError) as context:
            self.client.delete(
                f"users/teachers/teacher/{wrong_teacher_id}",
                headers=self.headers,
            )
        self.assertEqual(
            str(context.exception),
            PERMISSION_DENIED.format(str(self.teacher_id)),
        )
        self.teacher.id = self.teacher_id


if __name__ == "__main__":
    unittest.main()
