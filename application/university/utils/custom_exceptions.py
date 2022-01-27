class CreateUserException(Exception):
    def __init__(self, message):
        super(CreateUserException, self).__init__(message)


class UserSearchException(Exception):
    def __init__(self, message, status_code=400):
        super(UserSearchException, self).__init__(message)
        self.status_code = status_code
