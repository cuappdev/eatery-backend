from ..db import conn
from ..database import CollegetownEatery, CollegetownEateryHour
from ..gql_parser.common_eatery import parse_coordinates
from ..gql_types import (
    CollegetownEateryType,
    CollegetownEventType,
    CollegetownHoursType,
    PaymentMethodsType,
    PaymentMethodsEnum,
    RatingEnum,
)


def get_collegetown_eateries(eatery_id):
    """Queries db to fetch information about a specific or all collegetown eateries.

    Returns a list of CollegetownEateryType objects.
    """
    if eatery_id is not None:
        query = CollegetownEatery.query.filter_by(id=eatery_id)
    else:
        query = CollegetownEatery.query

    result = conn.execute(query.statement).fetchall()
    columns = CollegetownEatery.__table__.columns.keys()

    populated_result = []
    for data in result:
        mapped_eatery = {}
        for i, column_name in enumerate(columns):
            mapped_eatery[column_name] = data[i]
        populated_eatery = parse_collegetown_eateries(mapped_eatery)
        populated_result.append(populated_eatery)

    return populated_result


def parse_collegetown_eateries(eatery):
    """Parses eatery data from db and populates to an object.

    Returns a new CollegetownEateryType.
    """
    new_eatery = CollegetownEateryType(
        address=eatery.get("address", ""),
        categories=parse_categories(eatery),
        coordinates=parse_coordinates(eatery),
        eatery_type="Collegetown Restaurant",
        id=eatery.get("id"),
        image_url=eatery.get("image_url"),
        name=eatery.get("name", ""),
        operating_hours=parse_collegetown_hours(eatery),
        payment_methods=PaymentMethodsType(
            brbs=False, cash=True, cornell_card=False, credit=True, swipes=False, mobile=False
        ),
        payment_methods_enums=[PaymentMethodsEnum.CASH, PaymentMethodsEnum.CREDIT],
        phone=eatery.get("phone", "N/A"),
        price=eatery.get("price", ""),
        rating=eatery.get("rating", "N/A"),
        rating_enum=parse_rating(eatery),
        url=eatery.get("url", ""),
    )
    return new_eatery


def parse_rating(eatery):
    """Parses the rating of a Collegetown eatery.

    Returns the corresponding rating name according to the RatingEnum.
    """
    rating = eatery.get("rating", "N/A")
    index = int(round(float(rating) * 2))
    return RatingEnum.get(index)


def parse_categories(eatery):
    """Parses the restaurant category.

    Returns a list of strings.
    """
    categories = eatery.get("categories", "").split(",")
    return list(filter(lambda category: category != "", categories))


def parse_collegetown_hours(eatery):
    """Queries db for operating hours then parses the information into appropriate data format.

    Returns a list CollegetownHoursType objects.
    """
    query = CollegetownEateryHour.query.filter_by(eatery_id=eatery.get("id"))
    result = conn.execute(query.statement).fetchall()
    columns = CollegetownEateryHour.__table__.columns.keys()

    date_to_event = {}
    for data in result:
        mapped_hour = {}
        for i, column_name in enumerate(columns):
            mapped_hour[column_name] = data[i]

        hour_event = CollegetownEventType(
            description=mapped_hour.get("description", ""),
            end_time=mapped_hour.get("end_time", ""),
            start_time=mapped_hour.get("start_time", ""),
        )

        event_date = mapped_hour["date"]
        if event_date in date_to_event:
            date_to_event[event_date].append(hour_event)
        else:
            date_to_event[event_date] = [hour_event]

    populated_result = []
    dates_list = list(date_to_event.keys())
    for date in dates_list:
        new_hours = CollegetownHoursType(date=date, events=date_to_event.get(date, []))
        populated_result.append(new_hours)

    return populated_result
