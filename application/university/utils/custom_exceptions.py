class CreateUserException(Exception):
    def __init__(self, message):
        super(CreateUserException, self).__init__(message)
