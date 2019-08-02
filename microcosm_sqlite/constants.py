# Supplied to SQLAlchemy metadata to automatically generate names for
# constraints.  Otherwise Alembic migrations will fail.
naming_convention = dict(
    ix="ix_%(column_0_label)s",
    uq="uq_%(table_name)s_%(column_0_name)s",
    ck="ck_%(table_name)s_%(column_0_name)s",
    fk="fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    pk="pk_%(table_name)s",
)
