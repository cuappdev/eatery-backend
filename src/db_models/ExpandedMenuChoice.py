from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr


class ExpandedMenuChoice(object):
    @declared_attr
    def menu_item_id(cls):
        return Column(Integer, ForeignKey("expandedMenuItems.id"), nullable=False)

    id = Column(Integer, nullable=False, primary_key=True)
    label = Column(String, nullable=True)
    options = Column(String, nullable=True)
