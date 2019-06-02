class APIError(Exception):
    def __init__(self, error_type, error_kw='', message=''):
        super(APIError, self).__init__(message)
        self.error_type = error_type
        self.error_kw = error_kw
        self.message = message


class APIValueError(APIError):
    def __init__(self, field, message='The input value is invalid.'):
        super(APIValueError, self).__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    def __init__(self, field, message='Resource not found.'):
        super(APIResourceNotFoundError, self).__init__('value:not found', field, message)


class APIPermissionError(APIError):
    def __init__(self, message="Don't have permission to access."):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)
