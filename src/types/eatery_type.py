from graphene import Enum, Field, Float, Int, List, ObjectType, String

from src.types.expanded_menu_type import FoodCategoryType
from src.types.operating_hours_type import OperatingHoursType, CollegetownHoursType
from src.types.payment_methods_type import PaymentMethodsEnum, PaymentMethodsType
from src.types.swipe_data_type import SwipeDataType


class CampusAreaType(ObjectType):
    """ CampusAreaType

    description_short (String) -- Area of campus (e.g. North, West, Central)
    """

    description_short = String(required=True)


class CoordinatesType(ObjectType):
    """ CoordinatesType

    latitude (Float) -- Latitude information of eatery
    longitude (Float) -- Longitude information of eatery
    """

    latitude = Float(required=True)
    longitude = Float(required=True)


class RatingEnum(Enum):
    """ Represents a rating on a 1-5 scale with the constants representing double the rating value """

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
    """ EateryBaseType

    coordinates (CoordinatesType) -- Longitude and latitude information of eatery
    eatery_type (String) -- Type of eatery (e.g. Cafe, Food Court, All You Care To Eat Dining Room)
    id (Int) -- ID of eatery retrieved from cornell dining
    image_url (String) -- url of image to display on frontend
    name (String) -- Name of eatery
    payment_methods (PaymentMethodsType) -- Type of payments accepted in the particular eatery
    payment_methods_enums (List[PaymentMethodsEnum]) -- Enum of all type of payments accepted in eateries
    phone (String) -- Phone number of eatery
    """

    coordinates = Field(CoordinatesType, required=True)
    eatery_type = String(required=True)
    id = Int(required=True)
    image_url = String(required=True)
    name = String(required=True)
    payment_methods = Field(PaymentMethodsType, required=True)
    payment_methods_enums = List(PaymentMethodsEnum, required=True)
    phone = String(required=True)


class CampusEateryType(EateryBaseType):
    """ CampusEateryType

    about (String) -- Explanation of the eatery
    campus_area (CampusAreaType) -- Location of campus eatery
    expanded_menu (List[FoodCategory]) -- Menus in this eatery
    location (String) -- Building that the eatery is placed in
    name_short (String) -- Shortened name of eatery
    operating_hours (List[OperatingHoursType]) -- Operating hours of the eatery
    slug (String) -- Name of eatery that Cornell Dining provides; Same as Eatery name but is lower-case & hypens instead
                    of spaces
    swipe_data (List[SwipeDataType]) -- Swipe/wait-time information about the eatery
    """

    about = String(required=True)
    campus_area = Field(CampusAreaType, required=True)
    expanded_menu = List(FoodCategoryType, required=True)
    location = String(required=True)
    name_short = String(required=True)
    operating_hours = List(OperatingHoursType, required=True)
    slug = String(required=True)
    swipe_data = List(SwipeDataType, required=True)


class CollegetownEateryType(EateryBaseType):
    """ CollegetownEateryType

    address (String) -- Address of eatery
    categories (List[String]) -- Type of food eatery sells (e.g. Pizza, Groceries, Desserts, Coffee & Tea)
    operating_hours (List[CollegetownHoursType]) -- Operating hours of the eatery
    price (String) -- Price range (e.g. $, $$)
    rating (String) -- Star rating from Yelp
    rating_enum (RatingEnum) -- Enum of yelp star rating
    url (String) -- Yelp url of eatery
    """

    address = String(required=True)
    categories = List(String, required=True)
    operating_hours = List(CollegetownHoursType, required=True)
    price = String(required=True)
    rating = String(required=True)
    rating_enum = Field(RatingEnum, required=True)
    url = String(required=True)
