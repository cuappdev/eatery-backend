from graphene import List, ObjectType, String

from src.types.food_station_type import FoodStationType


class CollegetownEventType(ObjectType):
    """ CollegetownEventType

    description (String) -- Description of event
    end_time (String) -- Event end time (e.g. 2019-09-20:08:00PM)
    start_time (String) -- Event start time (e.g. 2019-09-20:08:00PM)
    """

    description = String(required=True)
    end_time = String(required=True)
    start_time = String(required=True)


class CollegetownHoursType(ObjectType):
    """ CollegetownHoursType

    date (String) -- Date (e.g. 2019-09-20)
    events (List[CollegetownEventType]) -- Event details for the corresponding date
    """

    date = String(required=True)
    events = List(CollegetownEventType, required=True)


class EventType(ObjectType):
    """ EventType

    cal_summary (String) -- Summary of event
    description (String) -- Description of event
    end_time (String) -- Event end time (e.g. 2019-09-20:08:00PM)
    menu (List[FoodStationType]) -- Menu item details
    start_time (String) -- Event start time (e.g. 2019-09-20:08:00PM)
    """

    cal_summary = String(required=True)
    description = String(required=True)
    end_time = String(required=True)  # <isodate>:<time>
    menu = List(FoodStationType, required=True)
    start_time = String(required=True)  # <isodate>:<time>


class OperatingHoursType(ObjectType):
    """ OperatingHoursType

    date (String) -- Date (e.g. 2019-09-20)
    events (List[EventType]) -- Event details for the corresponding date
    """

    date = String(required=True)
    events = List(EventType, required=True)
