

import ujson

from datetime import datetime as dt

from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

from twitter_geo.state_word_counts.utils import scan_paths
from twitter_geo.state_word_counts.db import session, engine


Base = declarative_base()
Base.query = session.query_property()


class StateCount(Base):

    __tablename__ = 'state_count'

    __table_args__ = dict(sqlite_autoincrement=True)

    id = Column(Integer, primary_key=True)

    key = Column(String, nullable=False, index=True)

    token = Column(String, nullable=False, index=True)

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
    def tokens(cls):
        """Get the set of unique tokens.

        Returns: set
        """
        query = session.query(cls.token).distinct()

        return set([r[0] for r in query])

    @classmethod
    def state_count(cls, state):
        """Get the total count for a state.

        Returns: int
        """
        return session \
            .query(func.sum(cls.count)) \
            .filter(cls.key==state) \
            .scalar()

    @classmethod
    def state_token_count(cls, state, token):
        """Get a token / state count.

        Returns: int
        """
        return session \
            .query(cls.count) \
            .filter(cls.key==state, cls.token==token) \
            .scalar()
