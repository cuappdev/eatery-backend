from sqlalchemy import Boolean, Column, Float, Integer, String
from .config import Base


class CampusEatery(Base):
    __tablename__ = "campusEateries"
    id = Column(Integer, nullable=False, primary_key=True)
    about = Column(String, nullable=False)
    campus_area_desc = Column(String, nullable=False)
    eatery_type = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    name_short = Column(String, nullable=False)
    payment_method_brbs = Column(Boolean, nullable=False)
    payment_method_cash = Column(Boolean, nullable=False)
    payment_method_cornell_card = Column(Boolean, nullable=False)
    payment_method_credit = Column(Boolean, nullable=False)
    payment_method_mobile = Column(Boolean, nullable=False)
    payment_method_swipes = Column(Boolean, nullable=False)
    phone = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    exceptions = Column(String, nullable=False)
