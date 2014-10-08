
class AuthenticationFailed(Exception):
    """
    Thrown to indicate that authentication has failed.
    """
    pass


class RequestFailed(Exception):
    """
    Thrown to indicate that request has failed.
    """
    def __init__(self, error_code, message):
        # Set some exception infomation
        self.error_code = error_code
        self.message = message
