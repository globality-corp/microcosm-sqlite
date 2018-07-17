"""
Custom types.

"""
from enum import Enum

from distutils.util import strtobool
from sqlalchemy.types import Boolean, TypeDecorator, Unicode


class EnumType(TypeDecorator):
    """
    SQLAlchemy enum type that persists the enum name (not value).

    Note that this type is very similar to the `ChoiceType` from `sqlalchemy_utils`,
    with the key difference being persisting by name (and not value).

    """
    impl = Unicode(255)

    def __init__(self, enum_class):
        self.enum_class = enum_class

    @property
    def python_type(self):
        return self.impl.python_type

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, Enum):
            return str(self.enum_class(value).name)
        return str(self.enum_class[value].name)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_class[value]


class Truthy(TypeDecorator):
    """
    Truthy-aware boolean value.

    Supports string-valued inputs (and handles them as gracefully as possible)

    """
    impl = Boolean

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if not value:
                return False
            return strtobool(value)
        return bool(value)
