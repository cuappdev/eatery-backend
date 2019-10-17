from .EateryBase import EateryBase
from sqlalchemy import Column, Integer, String


class CollegetownEatery(EateryBase):
    __tablename__ = "collegetownEateries"
    id = Column(Integer, nullable=False, primary_key=True)
    address = Column(String, nullable=False)
    categories = Column(String, nullable=False)
    price = Column(String, nullable=False)
    rating = Column(String, nullable=False)
    url = Column(String, nullable=False)
