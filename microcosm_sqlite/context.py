"""
Session context.

"""
from microcosm_sqlite.operations import new_session, recreate_all


class SessionContext:
    session = None

    def __init__(self, graph, expire_on_commit=False):
        self.graph = graph
        self.expire_on_commit = expire_on_commit

    def open(self):
        SessionContext.session = new_session(self.graph, self.expire_on_commit)
        return self

    def close(self):
        if SessionContext.session:
            SessionContext.session.close()
            SessionContext.session = None

    def commit(self):
        if SessionContext.session:
            SessionContext.session.commit()

    def rollback(self):
        if SessionContext.session:
            SessionContext.session.rollback()

    def recreate_all(self):
        """
        Recreate all database tables, but only in a testing context.
        """
        if self.graph.metadata.testing:
            recreate_all(self.graph)

    @classmethod
    def make(cls, graph, expire_on_commit=False):
        """
        Create an opened context.

        """
        return cls(graph, expire_on_commit).open()

    # context manager

    def __enter__(self):
        return self.open()

    def __exit__(self, *args, **kwargs):
        self.close()
