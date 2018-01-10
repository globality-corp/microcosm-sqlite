"""
Persistence errors.

Errors define a `status_code` for each translation to HTTP (because REST)
but are not coupled with any HTTP library.

"""


class SQLiteError(Exception):

    @property
    def status_code(self):
        return 500

    @property
    def include_stack_trace(self):
        return False


class ModelIntegrityError(SQLiteError):
    pass


class ModelNotFoundError(SQLiteError):

    @property
    def status_code(self):
        return 404


class DuplicateModelError(ModelIntegrityError):

    @property
    def status_code(self):
        return 409


class MultipleModelsFoundError(ModelIntegrityError):
    pass
