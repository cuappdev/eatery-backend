from src.parser.common_eatery import get_image_url, parse_coordinates, parse_payment_methods, parse_payment_methods_enum
from src.types import CampusAreaType, CampusEateryType


def parse_campus_eatery(eatery):
    """Parses eatery data from db and populates to an object of type CampusEateryType."""

    # dining_items = get_trillium_menu() if eatery_id == TRILLIUM_ID else parse_dining_items(eatery)

    new_eatery = CampusEateryType(
        about=eatery.get("about", ""),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        eatery_type=eatery.get("eatery_type", ""),
        # expanded_menu=parse_expanded_menu(eatery),
        id=eatery.get("id"),
        image_url=get_image_url(eatery),
        location=eatery.get("location", ""),
        name=eatery.get("name", ""),
        name_short=eatery.get("name_short", ""),
        # operating_hours=parse_operating_hours(eatery, dining_items),
        payment_methods=parse_payment_methods(eatery),
        payment_methods_enums=parse_payment_methods_enum(eatery),
        phone=eatery.get("phone", "N/A"),
        slug=eatery.get("slug", ""),
        # swipe_data=all_swipe_data.get(eatery.get("name", ""), []),
    )
    return new_eatery


def parse_campus_area(eatery):
    """Parses the common name location of an eatery.

    Returns a new CampusAreaType that contains a description of an eatery
    """
    campus_area = eatery.get("campus_area_desc", "")

    return CampusAreaType(description_short=campus_area)
