from .EateryBase import EateryBase
from sqlalchemy import Column, Integer, String


class CampusEatery(EateryBase):
    __tablename__ = "campusEateries"
    id = Column(Integer, nullable=False, primary_key=True)
    about = Column(String, nullable=False)
    campus_area_desc = Column(String, nullable=False)
    location = Column(String, nullable=False)
    name_short = Column(String, nullable=False)
    slug = Column(String, nullable=False)
