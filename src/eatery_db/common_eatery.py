from constants import IMAGES_URL


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
