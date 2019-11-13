from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from .config import Base


class SwipeData(Base):
    @declared_attr
    def eatery_id(cls):
        return Column(Integer, ForeignKey("campusEateries.id"), nullable=False)

    id = Column(Integer, nullable=False, primary_key=True)
    end_time = Column(String, nullable=False)
    session_type = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    swipe_density = Column(Float, nullable=False)
    wait_time_high = Column(Integer, nullable=False)
    wait_time_low = Column(Integer, nullable=False)
