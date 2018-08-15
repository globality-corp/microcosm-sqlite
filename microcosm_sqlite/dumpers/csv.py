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
        bulk_mode=False,
    ):
        self.graph = graph
        self.store = store
        self.defaults = dict()

    def default(self, **kwargs):
        self.defaults.update(kwargs)
        return self

    def dump(self, fileobj):
        writer = DictWriter(fileobj, fieldnames=self.get_columns())

        writer.writeheader()

        with self.store.model_class.new_context(self.graph):
            for item in self.store.search():
                writer.writerow(item._members())

    def get_columns(self):
        return {
            column.name: (key, column)
            for key, column in self.store.model_class.__mapper__.columns.items()
        }
