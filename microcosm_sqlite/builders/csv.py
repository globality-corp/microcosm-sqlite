"""
CSV-based building.

"""
from csv import DictReader


def get_columns(model_cls):
    return {
        column.name: (key, column)
        for key, column in model_cls.__mapper__.columns.items()
    }


def as_tuple(columns, name, value):
    key, column = columns[name]
    if not value and column.nullable:
        return key, None
    return key, value


def as_model(model_cls, row):
    columns = get_columns(model_cls)

    return model_cls(**dict(
        as_tuple(columns, name, value)
        for name, value in row.items()
        if name in columns
    ))


class CSVBuilder:
    """
    CSV-based builer for a single model class (non bulk mode)
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
        self.bulk_mode = bulk_mode

    def build(self, build_input):
        if self.bulk_mode:
            return self._build_in_bulk(build_input)
        else:
            return self._build(build_input)

    def bulk(self):
        self.bulk_mode = True

        return self

    def _build(self, fileobj):
        csv = DictReader(fileobj)

        with self.model_cls.new_context(self.graph) as context:
            for row in csv:
                model = as_model(self.model_cls, row)
                context.session.add(model)
            context.commit()

    def _build_in_bulk(self, model_fileobj):
        with self.model_cls.new_context(
            graph=self.graph,
            defer_foreign_keys=True,
        ) as context:
            for model_cls, fileobj in model_fileobj:
                reader = DictReader(fileobj)

                for row in reader:
                    context.session.add(
                        as_model(model_cls, row),
                    )

            context.session.commit()
