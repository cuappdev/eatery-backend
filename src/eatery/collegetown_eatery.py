from datetime import timedelta

from src.constants import NUM_DAYS_STORED_IN_DB
from src.eatery.common_eatery import (
    format_time,
    get_image_url,
    parse_coordinates,
    resolve_id,
    today
)
from src.types import (
    CollegetownEateryType,
    CollegetownEventType,
    CollegetownHoursType,
    PaymentMethodsEnum,
    PaymentMethodsType,
    RatingEnum
)

def parse_collegetown_eateries(collegetown_data, collegetown_eateries):
  """Parses Collegetown json dictionary.

  Fills the collegetown_eateries dictionary with objects of type CollegetownEateryType.

  Args:
      collegetown_data (dict): A valid json dictionary from Yelp that contains eatery information
      collegetown_eateries (dict): a dictionary to fill with collegetown eateries
  """
  for eatery in collegetown_data:
    new_id = resolve_id(eatery, collegetown=True)
    new_eatery = CollegetownEateryType(
        address=eatery['location']['address1'],
        categories=[cuisine['title'] for cuisine in eatery.get('categories', [])],
        coordinates=parse_coordinates(eatery),
        eatery_type='Collegetown Restaurant',
        id=new_id,
        image_url=get_image_url(eatery.get('alias', '')),
        name=eatery.get('name', ''),
        operating_hours=parse_collegetown_hours(eatery),
        payment_methods=PaymentMethodsType(
            brbs=False,
            cash=True,
            cornell_card=False,
            credit=True,
            swipes=False,
            mobile=False,
        ),
        payment_methods_enums=[PaymentMethodsEnum.CASH, PaymentMethodsEnum.CREDIT],
        phone=eatery.get('phone', 'N/A'),
        price=eatery.get('price', ''),
        rating=eatery.get('rating', 'N/A'),
        rating_enum=parse_rating(eatery),
        url=eatery.get('url', ''),
    )
    collegetown_eateries[new_eatery.id] = new_eatery

def parse_collegetown_hours(eatery):
  """Parses the hours of a Collegetown eatery.

  Returns a list of CollegetownHoursType. Calls parse_collegetown_events to fill the events field
  of CollegetownHoursType.

  Args:
      eatery (dict): A valid json dictionary from Yelp that contains eatery information
  """
  hours_list = eatery.get('hours', [{}])[0].get('open', [])
  # gets open hours from first dictionary in hours, empty dict-list provided to mimic hours format
  new_operating_hours = []

  for i in range(NUM_DAYS_STORED_IN_DB):
    new_date = today + timedelta(days=i)
    new_events = [event for event in hours_list if event['day'] == new_date.weekday()]
    new_operating_hours.append(
        CollegetownHoursType(
            date=new_date.isoformat(),
            events=parse_collegetown_events(new_events, new_date.isoformat())
        )
    )
  return new_operating_hours

def parse_collegetown_events(event_list, event_date):
  """Parses the events in a Collegetown eatery.

  Returns a list of CollegetownEventType.

  Args:
      event_list (list): Contains a list of times an eatery is open
      event_date (string): a string representation of the date
  """
  new_events = []
  for event in event_list:
    start, end = format_time(
        event.get('start', ''),
        event.get('end', ''),
        event_date,
        hr24=True,
        overnight=event.get('is_overnight', False)
    )
    new_event = CollegetownEventType(
        description='General',
        end_time=end,
        start_time=start,
    )
    new_events.append(new_event)
  return new_events

def parse_rating(eatery):
  """Parses the rating of a Collegetown eatery.

  Returns the corresponding rating name according to the RatingEnum.

  Args:
      eatery (dict): A valid json dictionary from Yelp that contains eatery information
  """
  rating = eatery.get('rating', 'N/A')
  index = int(round(float(rating) * 2))
  return RatingEnum.get(index)
