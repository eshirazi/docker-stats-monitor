from db import engine
from db_models.base import Base


def create_db_schema():
    # noinspection PyUnresolvedReferences
    from db_models import docker_stats_db_model
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_schema()
