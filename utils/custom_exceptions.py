class CreateException(Exception):
    def __init__(self, message):
        super(CreateException, self).__init__(message)


class UpdateException(Exception):
    def __init__(self, message, status_code=400):
        super(UpdateException, self).__init__(message)
        self.status_code = status_code


class SearchException(Exception):
    def __init__(self, message, status_code=404):
        super(SearchException, self).__init__(message)
        self.status_code = status_code


class NotProvided(Exception):
    def __init__(self, message, status_code=400):
        super(NotProvided, self).__init__(message)
        self.status_code = status_code


class InvalidCredentials(Exception):
    def __init__(self, message, status_code=400):
        super(InvalidCredentials, self).__init__(message)
        self.status_code = status_code
