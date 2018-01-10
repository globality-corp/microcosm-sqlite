# microcosm-sqlite

Opinionated data loading with SQLite.

While most distributed application runtimes will use a networked data store for mutable state,
the usage patterns of data that is read-only at runtime are great fit for SQLite.

In particular, `microcosm-sqlite` assumes that applications will

 -  Build data sets in advance and ship them as static artifacts (e.g. in source control)
 -  Load data immutable sets at runtime without loading entire data sets into memory
