from sqlalchemy import Boolean, Column, Float, Integer, String
from . import Base


class CollegetownEatery(Base):
    __tablename__ = "collegetownEateries"
    id = Column(Integer, nullable=False, primary_key=True)
    address = Column(String, nullable=False)
    categories = Column(String, nullable=False)
    eatery_type = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    payment_method_brbs = Column(Boolean, nullable=False)
    payment_method_cash = Column(Boolean, nullable=False)
    payment_method_cornell_card = Column(Boolean, nullable=False)
    payment_method_credit = Column(Boolean, nullable=False)
    payment_method_mobile = Column(Boolean, nullable=False)
    payment_method_swipes = Column(Boolean, nullable=False)
    phone = Column(String, nullable=False)
    price = Column(String, nullable=False)
    rating = Column(String, nullable=False)
    url = Column(String, nullable=False)
