from datetime import date, datetime, timedelta

from ..constants import IMAGES_URL
from ..database import ExpandedMenuStation, ExpandedMenuItem, ExpandedMenuChoice


def format_time(start_time, end_time, start_date, is_24_hour_time=False, overnight=False):
    """Returns a formatted time concatenated with date (string) for an eatery event

    Input comes in two forms depending on if it is collegetown eatery (24hr format).
    Some end times are 'earlier' than the start time, indicating we have rolled over to a new day.
    """
    if is_24_hour_time:
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


def get_image_url(slug):
    """Generates a URL for an image.

    Creates a string representing a url pointing towards the eatery image.

    Args:
        slug (string): a slugged name of an eatery
    """
    return "{}{}.jpg".format(IMAGES_URL, slug)


def parse_coordinates(eatery):
    """Parses the coordinates of an eatery.

    Returns a tuple containing the latitude and longitude.

    Args:
        eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
    """
    latitude, longitude = 0.0, 0.0
    if "coordinates" in eatery:
        latitude = eatery["coordinates"]["latitude"]
        longitude = eatery["coordinates"]["longitude"]
    return latitude, longitude


def parse_expanded_menu(menus, eatery_model):
    """Parses the expanded menu of an eatery.

    Returns a tuple of ExpandedMenuStation type available in the external expandedItems resource and the corresponding
    json for items

    Args:
        menu (dict): A valid json segment from the static expanded menu resource.
        eatery_model (CampusEatery): A valid campus eatery to which to link the menu object.
    """
    categories_and_items = []

    for menu in menus["eateries"]:
        for category in menu["categories"]:
            if eatery_model.slug != menu["slug"]:
                break
            for station in category["stations"]:
                menu_category = ExpandedMenuStation(
                    campus_eatery_id=eatery_model.id,
                    menu_category=category["category"],
                    station_category=station["station"],
                )
                categories_and_items.append((menu_category, station["diningItems"]))
    return categories_and_items


def parse_expanded_items(items, station_model):
    """Parses the expanded items for each station.

    Returns a tuple of ExpandedMenuItem type available at a station and the corresponding choices available for the
    choices

    Args:
        items (dict): A valid json segment from the hard-coded menu items
        station_model(ExpandedMenuChoice): A valid ExpandedMenuChoice item to which to bind the items.
    """
    items_and_choices = []
    for item in items:
        food_item = ExpandedMenuItem(
            station_category_id=station_model.id, healthy=False, item=item["item"], price=item["price"]
        )
        items_and_choices.append((food_item, item["choices"]))
    return items_and_choices


def parse_expanded_choices(item_choices, item_model):
    """Parses the options for an item.

    Returns the ExpandedMenuChoices for a given item

    Args:
        choices (dict): A valid json segment from the hard-coded menu items
        item_model (ExpandedMenuItem): A menu item to which to link the choices.
    """
    choices = []
    for choice in item_choices:
        item_choice = ExpandedMenuChoice(
            menu_item_id=item_model.id, label=choice["label"], options=str(choice["options"])[1:-1]
        )
        choices.append(item_choice)
    return choices


def string_to_date_range(dates):
    """
    dates: string representing a range of dates mm/dd/yy-mm/dd/yy
    """
    start_str, end_str = dates.split("-")
    start_date = datetime.strptime(start_str, "%m/%d/%y").date()
    end_date = datetime.strptime(end_str, "%m/%d/%y").date()
    return (start_date, end_date)
