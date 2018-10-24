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
        model_cls,
        bulk_mode=False,
    ):
        self.graph = graph
        self.model_cls = model_cls
        self.defaults = dict()

    def default(self, **kwargs):
        self.defaults.update(kwargs)
        return self

    def dump(self, fileobj, items=None):
        if items is None:
            items = self.model_cls.session.query(self.model_cls).all()
        writer = DictWriter(fileobj, fieldnames=self.get_columns())

        writer.writeheader()

        with self.model_cls.new_context(self.graph):
            for item in items:
                writer.writerow(item._members())

    def get_columns(self):
        return {
            column.name: (key, column)
            for key, column in self.model_cls.__mapper__.columns.items()
        }
