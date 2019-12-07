from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from .config import Base


class MenuCategory(Base):
    @declared_attr
    def event_id(cls):  # Null for dining items because they don't belong to a specific event
        return Column(Integer, ForeignKey("campusEateryHours.id"), nullable=True)

    @declared_attr
    def eatery_id(cls):
        return Column(Integer, ForeignKey("campusEateryHours.eatery_id"), nullable=False)

    __tablename__ = "menuCategories"
    id = Column(Integer, nullable=False, primary_key=True)
    category = Column(String, nullable=False)
