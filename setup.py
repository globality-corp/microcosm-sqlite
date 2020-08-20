#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm-sqlite"
version = "0.25.0"

setup(
    name=project,
    version=version,
    description="Opinionated persistence with SQLite",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-sqlite",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "SQLAlchemy-Utils>=0.33.3",
        "SQLAlchemy>=1.2.0",
        "alembic>=1.0.11",
        "microcosm>=2.12.0",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "sqlite = microcosm_sqlite.factories:SQLiteBindFactory",
            "sqlite_builder = microcosm_sqlite.builders:SQLiteBuilder",
            "sqlite_dumper = microcosm_sqlite.dumpers:SQLiteDumper",
        ],
    },
    extras_require={
        "lint": [
            "isort<5",
        ],
        "test": [
            "coverage>=3.7.1",
            "PyHamcrest>=1.8.5",
        ],
    },
)
