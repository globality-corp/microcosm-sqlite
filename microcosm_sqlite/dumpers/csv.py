"""
CSV-based building.

"""
from csv import DictWriter


class CSVDumper:
    """
    CSV-based builder for a single model class (non bulk mode)
    and multi model class (bulk mode).

    """
    def __init__(
        self,
        graph,
        store,
        model_cls=None,
    ):
        self.graph = graph
        self.store = store
        self.model_cls = model_cls or store.model_class
        self.defaults = dict()

    def default(self, **kwargs):
        self.defaults.update(kwargs)
        return self

    def dump(self, fileobj, items=None, fieldnames=None, extrasaction=None):
        if items is None:
            items = self.store.session.query(self.model_cls).all()

        writer = DictWriter(
            fileobj,
            fieldnames=fieldnames or self.get_columns(),
            extrasaction=extrasaction or 'raise',  # raise is the default
        )

        writer.writeheader()

        with self.model_cls.new_context(self.graph):
            for item in items:
                writer.writerow(item._members())

    def get_columns(self):
        return {
            key
            for key in self.model_cls.__mapper__.columns.keys()
        }
