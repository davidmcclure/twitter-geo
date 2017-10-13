

from invoke import task

from .db import engine
from .models import Base, StateCount


@task
def reset_db(ctx):
    """Recreate the bin counts database.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@task
def index_db(ctx):
    """Create indexes on bin counts database.
    """
    MinuteCount.add_indexes()
