from constants import IMAGES_URL
from datetime import date, datetime, timedelta

today = date.today()


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
