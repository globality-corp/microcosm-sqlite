"""
Custom types.

"""
from distutils.util import strtobool
from sqlalchemy.types import Boolean, TypeDecorator


class Truthy(TypeDecorator):
    """
    Truthy-aware boolean value.

    Supports string-valued inputs (and handles them as gracefully as possible)

    """
    impl = Boolean

    def process_bind_param(self, value, dialect):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if not value:
                return False
            return strtobool(value)
        return bool(value)
