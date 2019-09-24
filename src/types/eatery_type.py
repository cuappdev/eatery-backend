from graphene import Enum, Field, Float, Int, List, ObjectType, String

from src.types.expanded_menu_type import FoodCategoryType
from src.types.operating_hours_type import OperatingHoursType, CollegetownHoursType
from src.types.payment_methods_type import PaymentMethodsEnum, PaymentMethodsType
from src.types.swipe_data_type import SwipeDataType


class CampusAreaType(ObjectType):
    description_short = String(required=True)


class CoordinatesType(ObjectType):
    latitude = Float(required=True)
    longitude = Float(required=True)


class RatingEnum(Enum):
    # represents a rating on a 1-5 scale with the constants representing double the rating value
    ONE = 2
    ONE_HALF = 3
    TWO = 4
    TWO_HALF = 5
    THREE = 6
    THREE_HALF = 7
    FOUR = 8
    FOUR_HALF = 9
    FIVE = 10


class EateryBaseType(ObjectType):
    coordinates = Field(CoordinatesType, required=True)
    eatery_type = String(required=True)
    id = Int(required=True)
    image_url = String(required=True)
    name = String(required=True)
    payment_methods = Field(PaymentMethodsType, required=True)
    payment_methods_enums = List(PaymentMethodsEnum, required=True)
    phone = String(required=True)


class CampusEateryType(EateryBaseType):
    about = String(required=True)
    campus_area = Field(CampusAreaType, required=True)
    expanded_menu = List(FoodCategoryType, required=True)
    location = String(required=True)
    name_short = String(required=True)
    operating_hours = List(OperatingHoursType, required=True)
    slug = String(required=True)
    swipe_data = List(SwipeDataType, required=True)


class CollegetownEateryType(EateryBaseType):
    address = String(required=True)
    categories = List(String, required=True)
    operating_hours = List(CollegetownHoursType, required=True)
    price = String(required=True)
    rating = String(required=True)
    rating_enum = Field(RatingEnum, required=True)
    url = String(required=True)
