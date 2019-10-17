from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr


class CampusEateryHour(object):
    @declared_attr
    def eatery_id(cls):
        return Column(Integer, ForeignKey("campusEateries.id"), nullable=False)

    id = Column(Integer, nullable=False, primary_key=True)
    date = Column(String, nullable=False)
    event_description = Column(String, nullable=False)
    event_summary = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
