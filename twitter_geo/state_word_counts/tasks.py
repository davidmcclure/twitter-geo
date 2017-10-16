

from invoke import task

from twitter_geo.state_word_counts.db import engine
from twitter_geo.state_word_counts.models import Base, StateCount


@task
def reset_db(ctx):
    """Recreate the bin counts database.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@task
def load_db(ctx, path):
    """Load database.
    """
    StateCount.load(path)
