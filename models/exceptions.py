import re


class UniquenessConstraintViolatedException(Exception):
    def __init__(self, value=None):
        if value is None or re.match(r"^\s*$", value):
            value = "Attempt to add object to datastore would violate a uniqueness constraint"
        self.value = value

    def __str__(self):
        return repr(self.value)
