from sqlalchemy import Column, Integer, String, Float, DateTime

from db_models.base import Base


class DockerStatsDbModel(Base):
    __tablename__ = 'docker_stats'

    id = Column(Integer(), primary_key=True)
    container_id = Column(String(255), index=True)
    container_name = Column(String(255), index=True)
    timestamp = Column(DateTime(), index=True)
    stat_name = Column(String(255), index=True)
    stat_value = Column(Float())
