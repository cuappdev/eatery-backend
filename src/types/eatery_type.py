from graphene import Boolean, Field, Float, Int, List, ObjectType, String

from src.types.operating_hours_type import OperatingHoursType
from src.types.payment_methods_type import PaymentMethodsType

class CampusAreaType(ObjectType):
  description = String(required=True)
  description_short = String(required=True)

class CoordinatesType(ObjectType):
  latitude = Float(required=True)
  longitude = Float(required=True)

class EateryType(ObjectType):
  about = String(required=True)
  about_short = String(required=True)
  campus_area = Field(CampusAreaType, required=True)
  coordinates = Field(CoordinatesType, required=True)
  collegetown = Boolean(required=True)
  eatery_type = String(required=True)
  id = Int(required=True)
  image_url = String(required=True)
  location = String(required=True)
  name = String(required=True)
  name_short = String(required=True)
  operating_hours = List(OperatingHoursType, required=True)
  payment_methods = Field(PaymentMethodsType, required=True)
  phone = String(required=True)
  slug = String(required=True)
