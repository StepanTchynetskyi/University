from collections import namedtuple
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
NOT_FOUND_BY_ID = "{} with <id(s)={}> Not Found."
UPDATED_SUCCESSFULLY = "{} with <id={}> Updated Successfully."
SUCCESSFULLY_DELETED = "{} with <id={}> Deleted Successfully."
ALREADY_EXISTS = "{} with <{}> Already Exists."
ALREADY_EXISTS_WITH_YEAR = "{} with <name={}> and <year={}> Already Exists."
SOMETHING_WENT_WRONG = "Something Went Wrong {}."
NOT_ACTIVE_USER = "{} with <id={}> is not Active"
DATE_NOT_PROVIDED = "Error. Date Is Not Provided"
PERMISSION_DENIED = "Permission Denied <id={}>"
APPOINT_ITEM = "{} appointed to {}"
ITEM_NOT_PROVIDED = "{} Field Is Not Provided."
EMAIL_DOES_NOT_EXISTS = "User <email={}> Does Not Exist."

STUDENT = "Student"
TEACHER = "Teacher"
CURATOR = "Curator"
POSITION = "Position"
SPECIALTY = "Specialty"
SUBJECT = "Subject"
GROUP = "Group"

HAS_LOWERCASE_LETTERS = re.compile(r"[a-z]")
HAS_UPPERCASE_LETTERS = re.compile(r"[A-Z]")
HAS_NUMBERS = re.compile(r"[0-9]")
HAS_SYMBOLS = re.compile(r"[~`! @#$%^&*()_\-+={[}]|\:;\"\'<,>.?/]")
VALIDATE_EMAIL = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)

EntityInfo = namedtuple("EntityInfo", "id model schema type")
