

import ujson

from datetime import datetime as dt

from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import Index
from sqlalchemy.ext.declarative import declarative_base

from twitter_geo.core.models import Base
from twitter_geo.core.utils import scan_paths

from .db import session, engine


Base = declarative_base(cls=Base)
Base.query = session.query_property()


class StateCount(Base):

    __tablename__ = 'state_counts'

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

    @classmethod
    def add_indexes(cls):
        """Add indexes.
        """
        cls.add_index(cls.key)
        cls.add_index(cls.token)

    @classmethod
    def total_count(cls, state):
        """Get total count for state.
        """
        query = (
            session
            .query(func.sum(cls.count))
            .filter(func.key == state)
        )
