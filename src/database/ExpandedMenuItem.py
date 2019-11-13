from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from .config import Base


class ExpandedMenuItem(Base):
    @declared_attr
    def station_category_id(cls):
        return Column(Integer, ForeignKey("expandedMenuStations.id"), nullable=False)

    id = Column(Integer, nullable=False, primary_key=True)
    healthy = Column(Boolean, nullable=False)
    item = Column(String, nullable=False)
    price = Column(String, nullable=False)
