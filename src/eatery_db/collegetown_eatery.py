from .common_eatery import get_image_url, parse_coordinates

from database import CollegetownEatery


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
            categories=str([cuisine["title"] for cuisine in eatery.get("categories", [])]),
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
