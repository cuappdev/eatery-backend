from datetime import date, datetime, timedelta
import requests

from .common_eatery import get_image_url, parse_coordinates

from constants import PAY_METHODS, STATIC_MENUS_URL, TRILLIUM_SLUG

from database.CampusEatery import CampusEatery
from database.CampusEateryHour import CampusEateryHour
from database.MenuCategory import MenuCategory
from database.MenuItem import MenuItem


def parse_campus_eateries(data_json):
    """Parses a Cornell Dining json dictionary.

    Returns a list of CampusEatery objects containing on campus dining options.

    Args:
        data_json (dict): a valid dictionary from the Cornell Dining json
    """
    campus_eateries = []

    for eatery in data_json["data"]["eateries"]:
        brbs, cash, cornell_card, credit, mobile, swipes = parse_payments(eatery["payMethods"])
        phone = eatery.get("contactPhone", "N/A")
        phone = phone if phone else "N/A"  # handle None values
        latitude, longitude = parse_coordinates(eatery)

        new_eatery = CampusEatery(
            about=eatery.get("about", ""),
            campus_area_desc=parse_campus_area(eatery),
            eatery_type=parse_eatery_type(eatery),
            image_url=get_image_url(eatery.get("slug", "")),
            latitude=latitude,
            location=eatery.get("location", ""),
            longitude=longitude,
            name=eatery.get("name", ""),
            name_short=eatery.get("nameshort", ""),
            payment_method_brbs=brbs,
            payment_method_cash=cash,
            payment_method_cornell_card=cornell_card,
            payment_method_credit=credit,
            payment_method_mobile=mobile,
            payment_method_swipes=swipes,
            phone=phone,
            slug=eatery.get("slug", ""),
        )

        campus_eateries.append(new_eatery)

    return campus_eateries


def parse_campus_hours(data_json, eatery_model):
    """Parses a Cornell Dining json dictionary.

    Returns a list of tuples of CampusEateryHour objects for a corresponding CampusEatery object and their unparsed
    menu.

    Args:
        data_json (dict): a valid dictionary from the Cornell Dining json
        eatery_model (CampusEatery): the CampusEatery object to which to link the hours.
    """
    eatery_hours_and_menus = []

    for eatery in data_json["data"]["eateries"]:
        eatery_slug = eatery.get("slug")
        dining_items = get_trillium_menu() if eatery_slug == TRILLIUM_SLUG else parse_dining_items(eatery)

        if eatery_model.slug == eatery.get("slug", ""):
            hours_list = eatery["operatingHours"]

            for hours in hours_list:
                new_date = hours.get("date", "")
                hours_events = hours["events"]

                for event in hours_events:
                    start, end = format_time(event.get("start", ""), event.get("end", ""), new_date)

                    eatery_hour = CampusEateryHour(
                        eatery_id=eatery_model.id,
                        date=new_date,
                        event_description=event.get("descr", ""),
                        event_summary=event.get("calSummary", ""),
                        end_time=end,
                        start_time=start,
                    )

                    if not event["menu"] and dining_items:
                        event["menu"] = dining_items

                    eatery_hours_and_menus.append((eatery_hour, event.get("menu", [])))

    return eatery_hours_and_menus


def parse_menu_categories(menu_json, hour_model):
    """Parses the menu portion of the Cornell Dining json dictionary.

    Returns a tuple of a MenuCategory object linked to the provided CampusHours object and the unparsed items of that
    MenuCategory.

    Args:
        menu_json (dict): a valid dictionary from the Cornell Dining json
        hours_model (CampusHours): the CampusHours object to which to link the menu.
    """
    categories_and_items = []
    for menu in menu_json:
        if menu.get("category"):
            new_category = MenuCategory(event_id=hour_model.id, category=menu.get("category"))
            categories_and_items.append((new_category, menu.get("items", [])))
    return categories_and_items


def parse_menu_items(items_json, category_model):
    """
    Parses the items portion of the Cornell Dining json dictionary.

    Returns a list of MenuItems corresponding to a MenuCategory object.

    Args:
        items_json (dict): a valid dictionary from the Cornell Dining json
        category_model (MenuCategory): the MenuCategory object to which to link the menu.
    """
    items = []
    for item in items_json:
        new_item = MenuItem(
            category_id=category_model.id, healthy=item.get("healthy", False), item=item.get("item", "")
        )
        items.append(new_item)
    return items


def parse_campus_area(eatery):
    """Parses the common name location of an eatery.

    Returns a string containing a description of an eatery

    Args:
        eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
    """
    if "campusArea" in eatery:
        description_short = eatery["campusArea"]["descrshort"]
    return description_short


def parse_eatery_type(eatery):
    """Parses the classification of an eatery.

    Returns the type of an eatery (dining hall, cafe, etc).

    Args:
        eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
    """
    try:
        return eatery["eateryTypes"][0]["descr"]
    except Exception:
        return "Unknown"


def parse_payments(methods):
    """Returns a tuple containing Booleans corresponding to the payment methods are available at an
    eatery. Follows the format of <brbs>, <cash>, <credit>, <cornell>, <mobile>, <swipes>

    Args:
        methods (json): a valid json segment for payments from Cornell Dining
    """
    brbs = any(pay["descrshort"] == PAY_METHODS["brbs"] for pay in methods)
    cash = any(pay["descrshort"] == PAY_METHODS["credit"] for pay in methods)
    cornell_card = any(pay["descrshort"] == PAY_METHODS["c-card"] for pay in methods)
    credit = any(pay["descrshort"] == PAY_METHODS["credit"] for pay in methods)
    mobile = any(pay["descrshort"] == PAY_METHODS["mobile"] for pay in methods)
    swipes = any(pay["descrshort"] == PAY_METHODS["swipes"] for pay in methods)
    return brbs, cash, cornell_card, credit, mobile, swipes


def parse_dining_items(eatery):
    """Parses the dining items of an eatery.

    Returns a list that holds a dictionary for the items an eatery serves and a flag for healthy
    options. Exclusive to non-dining hall eateries.

    Args:
        eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
    """
    dining_items = {"items": []}
    for item in eatery["diningItems"]:
        dining_items["items"].append({"healthy": item.get("healthy", False), "item": item.get("item", "")})
    return [dining_items]


def get_trillium_menu():
    """Gets the Trillium menu.

    Returns the Trillium dining items (using parse_dining_items) from the static json source
    for menus.
    """
    static_json = requests.get(STATIC_MENUS_URL).json()
    return parse_dining_items(static_json["Trillium"][0])


def format_time(start_time, end_time, start_date, hr24=False, overnight=False):
    """Returns a formatted time concatenated with date (string) for an eatery event

    Input comes in two forms depending on if it is collegetown eatery (24hr format).
    Some end times are 'earlier' than the start time, indicating we have rolled over to a new day.
    """
    if hr24:
        start = datetime.strptime(start_time, "%H%M")
        start_time = start.strftime("%I:%M%p")
        end = datetime.strptime(end_time, "%H%M")
        end_time = end.strftime("%I:%M%p")

    else:
        start = datetime.strptime(start_time, "%H:%M%p")
        start_time = start.strftime("%I:%M") + start_time[-2:].upper()
        end = datetime.strptime(end_time, "%I:%M%p")
        end_time = end.strftime("%I:%M") + end_time[-2:].upper()

    end_date = start_date
    if overnight or (end.strftime("%p") == "AM" and end < start):
        year, month, day = start_date.split("-")
        next_day = date(int(year), int(month), int(day)) + timedelta(days=1)
        end_date = next_day.isoformat()

    new_start = "{}:{}".format(start_date, start_time)
    new_end = "{}:{}".format(end_date, end_time)

    return [new_start, new_end]
