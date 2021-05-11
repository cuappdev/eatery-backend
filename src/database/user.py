from sqlalchemy import Column, Float, ForeignKey, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declared_attr
from .config import PBase


class User(PBase):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True)
    netid = Column(String, nullable=False)
    favorites = Column(ARRAY(String), nullable=False)
