from sqlalchemy import Boolean, Column, Float, Integer, String


class EateryBase(object):
    id = Column(Integer, nullable=False, primary_key=True)
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
