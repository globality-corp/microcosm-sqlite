"""
Session context.

"""


class SessionContext:
    """
    A context manager for a shared session between subclasses of a DataSet.

    """
    def __init__(self, graph, data_set, expire_on_commit=False):
        self.graph = graph
        self.data_set = data_set
        self.expire_on_commit = expire_on_commit

    def open(self):
        self.data_set.session = self.data_set.new_session(
            self.graph,
            expire_on_commit=self.expire_on_commit,
        )
        return self

    def close(self):
        session = self.data_set.session
        if session:
            session.close()
            self.data_set.session = None

    def commit(self):
        session = self.data_set.session
        if session:
            session.commit()

    def rollback(self):
        session = self.data_set.session
        if session:
            session.rollback()

    # context manager

    def __enter__(self):
        return self.open()

    def __exit__(self, *args, **kwargs):
        self.close()
