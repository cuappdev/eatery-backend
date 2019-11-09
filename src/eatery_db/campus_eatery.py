from .common_eatery import get_image_url, parse_coordinates

from constants import PAY_METHODS

from database.CampusEatery import CampusEatery


def parse_campus_eateries(data_json):
    """Parses a Cornell Dining json dictionary.

    Returns a list of CampusEatery objects containing on campus dining options.

    Args:
        data_json (dict): a valid dictionary from the Cornell Dining json
        campus_eateries (dict): a dictionary to fill with campus eateries
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
