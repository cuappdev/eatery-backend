from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr


class MenuCategory(object):
    @declared_attr
    def event_id(cls):
        return Column(Integer, ForeignKey("campusEateryHours.id"), nullable=True)

    __tablename__ = "menuCategories"
    id = Column(Integer, nullable=False, primary_key=True)
    category = Column(String, nullable=False)
