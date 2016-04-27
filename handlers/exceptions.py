import re


class UnauthorizedException(Exception):
    def __init__(self, value=None):
        if value is None or re.match(r"^\s*$", str(value)):
            value = "User has not been authorized"
        self.value = value

    def __str__(self):
        return repr(self.value)


class NotRegisteredException(Exception):
    def __init__(self, value=None):
        if value is None or re.match(r"^\s*$", str(value)):
            value = "User is not registered"
        self.value = value

    def __str__(self):
        return repr(self.value)
