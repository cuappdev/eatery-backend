from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from .config import Base


class ExpandedMenuStation(Base):
    @declared_attr
    def campus_eatery_id(cls):
        return Column(Integer, ForeignKey("campusEateries.id"), nullable=False)

    id = Column(Integer, nullable=False, primary_key=True)
    menu_category = Column(String, nullable=False)
    station_category = Column(String, nullable=False)
