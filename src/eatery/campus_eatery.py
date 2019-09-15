import requests

from src.constants import STATIC_MENUS_URL, TRILLIUM_ID
from src.types import CampusEateryType, OperatingHoursType
from src.eatery.common_eatery import (
    get_image_url,
    parse_campus_area,
    parse_coordinates,
    parse_dining_items,
    parse_eatery_type,
    parse_events,
    parse_expanded_menu,
    parse_payment_methods,
    parse_payment_methods_enum,
    resolve_id,
)


def parse_eatery(data_json, campus_eateries, all_swipe_data):
    """Parses a Cornell Dining json dictionary.

  Fills the campus_eateries dictionary with objects of type CampusEateryType.

  Args:
      data_json (dict): a valid dictionary from the Cornell Dining json
      campus_eateries (dict): a dictionary to fill with campus eateries
  """
    for eatery in data_json["data"]["eateries"]:
        eatery_id = eatery.get("id", resolve_id(eatery))
        dining_items = get_trillium_menu() if eatery_id == TRILLIUM_ID else parse_dining_items(eatery)
        phone = eatery.get("contactPhone", "N/A")
        phone = phone if phone else "N/A"  # handle None values

        new_eatery = CampusEateryType(
            about=eatery.get("about", ""),
            campus_area=parse_campus_area(eatery),
            coordinates=parse_coordinates(eatery),
            eatery_type=parse_eatery_type(eatery),
            expanded_menu=parse_expanded_menu(eatery),
            id=eatery_id,
            image_url=get_image_url(eatery.get("slug", "")),
            location=eatery.get("location", ""),
            name=eatery.get("name", ""),
            name_short=eatery.get("nameshort", ""),
            operating_hours=parse_operating_hours(eatery, dining_items),
            payment_methods=parse_payment_methods(eatery["payMethods"]),
            payment_methods_enums=parse_payment_methods_enum(eatery.get("payMethods", [])),
            phone=phone,
            slug=eatery.get("slug", ""),
            swipe_data=all_swipe_data.get(eatery.get("name", ""), []),
        )
        campus_eateries[new_eatery.id] = new_eatery


def get_trillium_menu():
    """Gets the Trillium menu.

  Returns the Trillium dining items (using parse_dining_items) from the static json source
  for menus.
  """
    static_json = requests.get(STATIC_MENUS_URL).json()
    return parse_dining_items(static_json["Trillium"][0])


def parse_operating_hours(eatery, dining_items):
    """Returns a list of OperatingHoursTypes for each dining event for an eatery.

  Calls parse_events to populate the events field for OperatingHoursType.

  Args:
      eatery (dict): A valid json segment from Cornell Dining that contains eatery information
      dining_items (list): A list that holds a dictionary for the items an eatery serves and a flag
       for healthy options
  """
    new_operating_hours = []
    hours_list = eatery["operatingHours"]
    for hours in hours_list:
        new_date = hours.get("date", "")
        hours_events = hours["events"]
        # merge the dining items from the json (for non-dining hall eateries) with the menu for an event
        for event in hours_events:
            if not event["menu"] and dining_items:
                event["menu"] = dining_items

        new_operating_hour = OperatingHoursType(date=new_date, events=parse_events(hours_events, new_date))
        new_operating_hours.append(new_operating_hour)
    return new_operating_hours
