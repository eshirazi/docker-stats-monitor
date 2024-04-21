import os

from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy.types import CLOB


engine = create_engine(os.environ["DATABASE_URL"])


def get_db_engine():
    return engine


def get_db_session(connection=None):
    if connection is None:
        return Session(bind=get_db_engine())
    else:
        return Session(bind=connection)
