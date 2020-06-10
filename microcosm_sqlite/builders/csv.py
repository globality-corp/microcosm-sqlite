"""
CSV-based building.

"""
from csv import DictReader

from sqlalchemy.sql.expression import delete, text


class CSVBuilder:
    """
    CSV-based builder for a single model class (non bulk mode)
    and multi model class (bulk mode).

    """
    def __init__(
        self,
        graph,
        model_cls,
        bulk_mode=False,
        commit_on_insert=False,
        delete_before_load=False,
    ):
        self.graph = graph
        self.model_cls = model_cls
        self.bulk_mode = bulk_mode
        self.commit_on_insert = commit_on_insert
        self.delete_before_load = delete_before_load
        self.defaults = dict()

    def build(self, build_input):
        if self.bulk_mode:
            return self._build_in_bulk(build_input)
        else:
            return self._build(build_input)

    def bulk(self):
        self.bulk_mode = True
        return self

    def default(self, **kwargs):
        self.defaults.update(kwargs)
        return self

    def delete_all(self, model_class, session):
        # NB not using store, as for some models, e.g. the ones
        # resulting from a mixins, we don't have a store.
        return session.execute(
            delete(text(model_class.__tablename__)),
        )

    def _build(self, fileobj):
        csv = DictReader(fileobj)

        with self.model_cls.new_context(self.graph) as context:
            if self.delete_before_load:
                self.delete_all(self.model_cls, context.session)

            for row in csv:
                model = self.as_model(self.model_cls, row)
                context.session.add(model)
                if self.commit_on_insert:
                    # Commit rows individually
                    context.commit()

            if not self.commit_on_insert:
                context.commit()

    def _build_in_bulk(self, model_fileobj):
        with self.model_cls.new_context(
            graph=self.graph,
            defer_foreign_keys=True,
        ) as context:
            for model_cls, fileobj in model_fileobj:
                if self.delete_before_load:
                    self.delete_all(model_cls, context.session)

                reader = DictReader(fileobj)

                for row in reader:
                    context.session.add(
                        self.as_model(model_cls, row),
                    )
                    if self.commit_on_insert:
                        # Commit rows individually
                        context.session.commit()

            if not self.commit_on_insert:
                context.session.commit()

    def as_model(self, model_cls, row):
        columns = self.get_columns(model_cls)

        row_dict = self.defaults.copy()
        row_dict.update(row)

        return model_cls(**dict(
            self.as_tuple(columns, name, value)
            for name, value in row_dict.items()
            if name in columns
        ))

    @staticmethod
    def get_columns(model_cls):
        return {
            column.name: (key, column)
            for key, column in model_cls.__mapper__.columns.items()
        }

    @staticmethod
    def as_tuple(columns, name, value):
        key, column = columns[name]
        if not value and column.nullable:
            return key, None
        return key, value
