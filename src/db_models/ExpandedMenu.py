from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr


class ExpandedMenu(object):
    @declared_attr
    def campus_eatery_id(cls):
        return Column(Integer, ForeignKey("campusEateries.id"), nullable=True)

    @declared_attr
    def campus_hour_id(cls):
        return Column(Integer, ForeignKey("campusEateryHours.id"), nullable=True)

    @declared_attr
    def collegetown_eatery_id(cls):
        return Column(Integer, ForeignKey("collegetownEateries.id"), nullable=True)

    @declared_attr
    def collegetown_hour_id(cls):
        return Column(Integer, ForeignKey("collegetownEateryHours.id"), nullable=True)

    id = Column(Integer, nullable=False, primary_key=True)
    choices = Column(String, nullable=True)
    healthy = Column(Boolean, nullable=False)
    item = Column(String, nullable=False)
    menu_category = Column(String, nullable=False)
    price = Column(String, nullable=False)
    station_category = Column(String, nullable=False)