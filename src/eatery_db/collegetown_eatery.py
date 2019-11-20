from datetime import timedelta

from .common_eatery import format_time, get_image_url, parse_coordinates, today

from constants import NUM_DAYS_STORED_IN_DB, STATIC_CTOWN_HOURS_URL

from database import CollegetownEatery, CollegetownEateryHour

import requests


def parse_collegetown_eateries(collegetown_data):
    """Parses a Collegetown json dictionary.

    Returns a list of Collegetown objects containing Collegetown dining options.

    Args:
        collegetown_data (dict): A valid json dictionary from Yelp that contains eatery information
  """
    collegetown_eateries = []

    for eatery in collegetown_data:
        latitude, longitude = parse_coordinates(eatery)

        new_eatery = CollegetownEatery(
            address=eatery["location"]["address1"],
            categories=str([cuisine["title"] for cuisine in eatery.get("categories", [])])[1:-1],
            eatery_type="Collegetown Restaurant",
            image_url=get_image_url(eatery.get("alias", "")),
            latitude=latitude,
            longitude=longitude,
            name=eatery.get("name", ""),
            payment_method_brbs=False,
            payment_method_cash=True,
            payment_method_cornell_card=False,
            payment_method_credit=True,
            payment_method_mobile=False,
            payment_method_swipes=False,
            phone=eatery.get("phone", "N/A"),
            price=eatery.get("price", ""),
            rating=str(eatery.get("rating", "N/A")),
            url=eatery.get("url", ""),
        )

        collegetown_eateries.append(new_eatery)

    return collegetown_eateries


def parse_collegetown_hours(data_json, eatery_model):
    for eatery in data_json:
        if eatery_model.url == eatery.get("url", ""):
            hours_list = eatery.get("hours", [{}])[0].get("open", [])
            # gets open hours from first dictionary in hours, empty dict-list provided to mimic hours format

            eatery_alias = eatery.get("alias", "")
            # these hours are not on Yelp and need to be queried from another source
            static_eateries = requests.get(STATIC_CTOWN_HOURS_URL).json()
            for static_eatery in static_eateries["eateries"]:
                if static_eatery["alias"] == eatery_alias:
                    hours_list = static_eatery.get("hours", [{}])[0].get("open", [])
                    break

            new_operating_hours = []

            for i in range(NUM_DAYS_STORED_IN_DB):
                new_date = today + timedelta(days=i)
                new_events = [event for event in hours_list if event["day"] == new_date.weekday()]
                for event in new_events:
                    start, end = format_time(
                        event.get("start", ""),
                        event.get("end", ""),
                        new_date.isoformat(),
                        hr24=True,
                        overnight=event.get("is_overnight", False),
                    )
                    new_operating_hours.append(
                        CollegetownEateryHour(
                            eatery_id=eatery_model.id,
                            date=new_date.isoformat(),
                            event_description="General",
                            end_time=end,
                            start_time=start,
                        )
                    )
            return new_operating_hours
    return []
