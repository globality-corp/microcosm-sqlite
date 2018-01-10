"""
Model base classes and mixins.

"""
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base(name="sqlite")


class Model(Base):
    """
    Abstract model with basic equality functions.

    This form of equality isn't always appropriate, but it's a good place to start,
    especially for writing test assertions.

    """
    __abstract__ = True

    def _members(self):
        """
        Return a dict of non-private members.

        """
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    def __eq__(self, other):
        return type(other) is type(self) and self._members() == other._members()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self) if self.uri is None else hash(self.uri)
