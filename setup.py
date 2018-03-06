#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm-sqlite"
version = "0.3.0"

setup(
    name=project,
    version=version,
    description="Opinionated persistence with SQLite",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-sqlite",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="microcosm",
    install_requires=[
        "microcosm>=2.0.0",
        "SQLAlchemy>=1.2.0",
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
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "mock>=2.0.0",
        "PyHamcrest>=1.8.5",
    ],
)
