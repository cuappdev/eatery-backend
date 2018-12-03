from graphene import Field, Float, Int, List, ObjectType, String

from src.types.operating_hours_type import OperatingHoursType, CollegetownHoursType
from src.types.payment_methods_type import PaymentMethodsType

class CampusAreaType(ObjectType):
  description = String(required=True)
  description_short = String(required=True)

class CoordinatesType(ObjectType):
  latitude = Float(required=True)
  longitude = Float(required=True)

class EateryBaseType(ObjectType):
  coordinates = Field(CoordinatesType, required=True)
  eatery_type = String(required=True)
  id = Int(required=True)
  image_url = String(required=True)
  name = String(required=True)
  payment_methods = Field(PaymentMethodsType, required=True)
  phone = String(required=True)

class CampusEateryType(EateryBaseType):
  about = String(required=True)
  about_short = String(required=True)
  campus_area = Field(CampusAreaType, required=True)
  location = String(required=True)
  name_short = String(required=True)
  operating_hours = List(OperatingHoursType, required=True)
  slug = String(required=True)

class CollegetownEateryType(EateryBaseType):
  address = String(required=True)
  categories = List(String, required=True)
  operating_hours = List(CollegetownHoursType, required=True)
  price = String(required=True)
  rating = String(required=True)
  url = String(required=True)
