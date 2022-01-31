class CreateUserException(Exception):
    def __init__(self, message):
        super(CreateUserException, self).__init__(message)


class SearchException(Exception):
    def __init__(self, message, status_code=400):
        super(SearchException, self).__init__(message)
        self.status_code = status_code
