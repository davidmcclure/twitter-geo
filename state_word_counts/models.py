

import ujson

from datetime import datetime as dt

from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import Index
from sqlalchemy.ext.declarative import declarative_base

from .utils import scan_paths
from .db import session, engine


Base = declarative_base()
Base.query = session.query_property()


class StateCount(Base):

    __tablename__ = 'word_counts'

    __table_args__ = dict(sqlite_autoincrement=True)

    id = Column(Integer, primary_key=True)

    key = Column(String, nullable=False)

    token = Column(String, nullable=False)

    count = Column(Integer, nullable=False)

    @classmethod
    def load(cls, root):
        """Bulk-insert rows from CSVs.
        """
        for path in scan_paths(root, '\.json$'):
            with open(path) as fh:

                segment = [ujson.loads(line) for line in fh]
                session.bulk_insert_mappings(cls, segment)

                session.commit()
                print(dt.now(), path)

    # TODO: Move to base class.
    @classmethod
    def add_index(cls, *cols, **kwargs):
        """Add an index to the table.
        """
        # Make slug from column names.
        col_names = '_'.join([c.name for c in cols])

        # Build the index name.
        name = 'idx_{}_{}'.format(cls.__tablename__, col_names)

        idx = Index(name, *cols, **kwargs)

        # Render the index.
        try:
            idx.create(bind=engine)
        except Exception as e:
            print(e)

        print(col_names)

    @classmethod
    def add_indexes(cls):
        """Add indexes.
        """
        cls.add_index(cls.key)
        cls.add_index(cls.token)
