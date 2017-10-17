

import glob
import ujson
import os
import click

from collections import OrderedDict

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, event, Column, Integer, String, func
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base


db_path = os.path.join(os.path.dirname(__file__), 'data.db')
url = URL(drivername='sqlite', database=db_path)
engine = create_engine(url)
factory = sessionmaker(bind=engine)
session = scoped_session(factory)


Base = declarative_base()
Base.query = session.query_property()


class StateWordCount(Base):

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
        for path in glob.glob(os.path.join(root, '*.json')):
            with open(path) as fh:

                segment = [ujson.loads(line) for line in fh]
                session.bulk_insert_mappings(cls, segment)

                session.commit()
                print(path)

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
    def state_counts(cls):
        """Get all state -> count pairs.

        Returns: int
        """
        query = session \
            .query(cls.key, func.sum(cls.count)) \
            .group_by(cls.key)

        return OrderedDict(query.all())

    @classmethod
    def state_token_count(cls, state, token):
        """Get a token / state count.

        Returns: int
        """
        return session \
            .query(cls.count) \
            .filter(cls.key==state, cls.token==token) \
            .scalar()


@click.group()
def cli():
    pass


@cli.command()
def create():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@cli.command()
@click.argument('path', type=click.Path())
def load(path):
    StateWordCount.load(path)


if __name__ == '__main__':
    cli()
