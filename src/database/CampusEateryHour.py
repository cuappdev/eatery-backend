from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from .config import Base


class CampusEateryHour(Base):
    @declared_attr
    def eatery_id(cls):
        return Column(Integer, ForeignKey("campusEateries.id"), nullable=False)

    id = Column(Integer, nullable=False, primary_key=True)
    date = Column(String, nullable=False)
    event_description = Column(String, nullable=True)
    event_summary = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    start_time = Column(String, nullable=True)
