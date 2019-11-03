from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr


class MenuItem(object):
    @declared_attr
    def category_id(cls):
        return Column(Integer, ForeignKey("menuCategories.id"), nullable=True)

    id = Column(Integer, nullable=False, primary_key=True)
    healthy = Column(Boolean, nullable=False)
    item = Column(String, nullable=False)
