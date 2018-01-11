# microcosm-sqlite

Opinionated data loading with SQLite.

While most distributed application runtimes will use a networked data store for mutable state,
the usage patterns of data that is read-only at runtime are great fit for SQLite.

In particular, `microcosm-sqlite` assumes that applications will

 -  Build data sets in advance and ship them as static artifacts (e.g. in source control)
 -  Load data immutable sets at runtime without loading entire data sets into memory


## Writing Models

Persistent data is expected to use SQLAlchemy's declarative base classes. Because different data sets
may be shipped in different SQLite databases, each declarative base class needs to have a **unique**
name and a separate engine configuration, which is achieved by adding `DataSet` as the base of the
declarative base class:

    Base = DataSet.create("some_name")


    class SomeModel(Base):
        __tablename__ = "sometable"

        id = Column(Integer, primary_key=True)


## Using Stores

Basic persistence operations are abstracted through a store:

    class SomeStore(Store):

        @property
        def model_class(self):
            return SomeModel


     store = SomeStore()
     results = store.search()


## Configuring SQLite

Each `DataSet` defaults to using `:memory:` storage, but can be customized in two ways:

 1. The `SQLiteBindFactory` can be configured with custom paths:

        loader = load_from_dict(
            sqlite=dict(
                paths={
                    "some_name": "/path/to/database",
                },
            ),
        )
        graph = create_object_graph("example", loader=loader)

 2. The `microcosm.sqlite` entrypoint can contain a mapping from a data set name to a
    function that returns a path.
