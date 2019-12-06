from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from .config import Base


class MenuItem(Base):
    @declared_attr
    def category_id(cls):
        return Column(Integer, ForeignKey("menuCategories.id"), nullable=True)

    id = Column(Integer, nullable=False, primary_key=True)
    healthy = Column(Boolean, nullable=False)
    item = Column(String, nullable=False)
