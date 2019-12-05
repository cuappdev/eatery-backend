from graphene import List, ObjectType, String

from .food_station_type import FoodStationType


class CollegetownEventType(ObjectType):
    description = String(required=True)
    end_time = String(required=True)
    start_time = String(required=True)


class CollegetownHoursType(ObjectType):
    date = String(required=True)
    events = List(CollegetownEventType, required=True)


class EventType(ObjectType):
    cal_summary = String(required=True)
    description = String(required=True)
    end_time = String(required=True)  # <isodate>:<time>
    menu = List(FoodStationType, required=True)
    start_time = String(required=True)  # <isodate>:<time>


class OperatingHoursType(ObjectType):
    date = String(required=True)
    events = List(EventType, required=True)
