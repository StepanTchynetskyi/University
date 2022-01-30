import re

MAX_EMAIL_LENGTH = 320
MAX_FIRST_NAME_LENGTH = 60
MAX_LAST_NAME_LENGTH = 80
MAX_NAME_LENGTH = 60
MAX_PASSWORD_LENGTH = 72


PW_DO_NOT_MATCH = "Passwords Do Not Match."
CREATED_SUCCESSFULLY = "{} <id={}> Created Successfully."
POSITION_ID_NOT_PROVIDED = "Position Id Not Provided."
DOES_NOT_EXIST = "{} <id={}> Does Not Exist."
NOT_FOUND_BY_ID = "{} with <id={}> Not Found."
UPDATED_SUCCESSFULLY = "{} with <id={}> Updated Successfully."
SUCCESSFULLY_DELETED = "{} with <id={}> Deleted Successfully."
ALREADY_EXIST = "{} with <{}> Already Exists."
SOMETHING_WENT_WRONG = "Something Went Wrong {}."
NOT_ACTIVE_USER = "{} with <id={}> is not Active"
DATE_NOT_PROVIDED = "Error. Date Is Not Provided"

STUDENT = "Student"
TEACHER = "Teacher"
POSITION = "Position"
SPECIALTY = "Specialty"

HAS_LOWERCASE_LETTERS = re.compile(r"[a-z]")
HAS_UPPERCASE_LETTERS = re.compile(r"[A-Z]")
HAS_NUMBERS = re.compile(r"[0-9]")
HAS_SYMBOLS = re.compile(r"[~`! @#$%^&*()_\-+={[}]|\:;\"\'<,>.?/]")
VALIDATE_EMAIL = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)
