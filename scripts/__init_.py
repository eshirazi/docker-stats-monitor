from sqlalchemy.orm import Session
from db import engine
from db_models.base import Base


def create_db_schema():
    # noinspection PyUnresolvedReferences
    import db_models.all
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_schema()
