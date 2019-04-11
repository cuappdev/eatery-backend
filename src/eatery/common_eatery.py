from datetime import date, datetime, timedelta

from src.constants import (
    IMAGES_URL,
    PAY_METHODS
)
from src.types import (
    CampusAreaType,
    CoordinatesType,
    EventType,
    FoodItemType,
    FoodStationType,
    PaymentMethodsType
)

today = date.today()
static_eateries = {}

def parse_campus_area(eatery):
  """Parses the common name location of an eatery.

  Returns a new CampusAreaType that contains a description of an eatery

  Args:
      eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
  """
  if 'campusArea' in eatery:
    description_short = eatery['campusArea']['descrshort']
  return CampusAreaType(
      description_short=description_short
  )

def parse_coordinates(eatery):
  """Parses the coordinates of an eatery.

  Returns a new CoordinateType that holds the geographic coordinates of an eatery.

  Args:
      eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
  """
  latitude, longitude = 0.0, 0.0
  if 'coordinates' in eatery:
    latitude = eatery['coordinates']['latitude']
    longitude = eatery['coordinates']['longitude']
  return CoordinatesType(
      latitude=latitude,
      longitude=longitude,
  )

def parse_dining_items(eatery):
  """Parses the dining items of an eatery.

  Returns a list that holds a dictionary for the items an eatery serves and a flag for healthy
  options. Exclusive to non-dining hall eateries.

  Args:
      eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
  """
  dining_items = {'items': []}
  for item in eatery['diningItems']:
    dining_items['items'].append({
        'healthy': item.get('healthy', False),
        'item': item.get('item', '')
    })
  return [dining_items]

def parse_eatery_type(eatery):
  """Parses the classification of an eatery.

  Returns the type of an eatery (dining hall, cafe, etc).

  Args:
      eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
  """
  try:
    return eatery['eateryTypes'][0]['descr']
  except Exception:
    return 'Unknown'

def parse_events(event_list, event_date):
  """Parses the events of an eatery.

  Returns a list of EventType for each event of an eatery. Calls parse_food_stations to populate
  the menu field for EventType.

  Args:
      event_list (list): The list of all events for an eatery
      event_date (string): The date of all of the events of the eatery
  """
  new_events = []
  for event in event_list:
    start, end = format_time(event.get('start', ''), event.get('end', ''), event_date)
    new_event = EventType(
        cal_summary=event.get('calSummary', ''),
        description=event.get('descr', ''),
        end_time=end,
        menu=parse_food_stations(event.get('menu', [])),
        start_time=start
    )
    new_events.append(new_event)
  return new_events

def parse_payment_methods(methods):
  """Returns a PaymentMethodsType according to which payment methods are available at an eatery.

  Args:
      methods (json): a valid json segment for payments from Cornell Dining
  """
  payment_methods = PaymentMethodsType()
  payment_methods.brbs = any(pay['descrshort'] == PAY_METHODS['brbs'] for pay in methods)
  payment_methods.cash = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.credit = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.cornell_card = any(pay['descrshort'] == PAY_METHODS['c-card'] for pay in methods)
  payment_methods.mobile = any(pay['descrshort'] == PAY_METHODS['mobile'] for pay in methods)
  payment_methods.swipes = any(pay['descrshort'] == PAY_METHODS['swipes'] for pay in methods)
  return payment_methods

def parse_food_stations(station_list):
  """Parses the food stations available at an event

  Returns a list containing FoodStationTypes for an eatery. Calls parse_food_items to populate
  the items field for FoodStationType.

  Args:
      station_list (list): A list representing all of the stations in a dining hall
  """
  new_stations = []
  if len(station_list) == 1 and not station_list[0]['items']:  # no menu actually provided
    return new_stations
  for station in station_list:
    new_station = FoodStationType(
        category=station.get('category', ''),
        items=parse_food_items(station.get('items', []))
    )
    new_stations.append(new_station)
  return new_stations

def parse_food_items(item_list):
  """Parses the food items available at a food station.

  Returns a list containing FoodItemTypes for an eatery. This is the lowest level that
  is parsed for a dining hall.

  Args:
      item_list (list): A list representing the individual food items for each station
  """
  new_food_items = []
  for item in item_list:
    new_food_items.append(
        FoodItemType(
            healthy=item.get('healthy', False),
            item=item.get('item', '')
        )
    )
  return new_food_items

def resolve_id(eatery, collegetown=False):
  """Returns a new id (int) for an external eatery
  If the eatery does not have a provided id, we need to create one.
  Since all provided eatery ID values are positive, we decrement starting at 0.
  """
  if not collegetown and 'id' in eatery:
    return eatery['id']
  elif eatery['name'] in static_eateries:
    return static_eateries[eatery['name']]
  new_id = -1 * len(static_eateries)
  static_eateries[eatery['name']] = new_id
  return new_id

def get_image_url(slug):
  """Generates a URL for an image.

  Creates a string that represents a url pointing towards the eatery image.

  Args:
      slug (string): a slugged name of an eatery
  """
  return "{}{}.jpg".format(IMAGES_URL, slug)

def format_time(start_time, end_time, start_date, hr24=False, overnight=False):
  """Returns a formatted time concatenated with date (string) for an eatery event
  Input comes in two forms depending on if it is collegetown eatery (24hr format).
  Some end times are 'earlier' than the start time, indicating we have rolled over to a new day.
  """
  if hr24:
    start = datetime.strptime(start_time, '%H%M')
    start_time = start.strftime('%I:%M%p')
    end = datetime.strptime(end_time, '%H%M')
    end_time = end.strftime('%I:%M%p')

  else:
    start = datetime.strptime(start_time, '%H:%M%p')
    start_time = start.strftime('%I:%M') + start_time[-2:].upper()
    end = datetime.strptime(end_time, '%I:%M%p')
    end_time = end.strftime('%I:%M') + end_time[-2:].upper()

  end_date = start_date
  if overnight or (end.strftime('%p') == 'AM' and end < start):
    year, month, day = start_date.split('-')
    next_day = date(int(year), int(month), int(day)) + timedelta(days=1)
    end_date = next_day.isoformat()

  new_start = "{}:{}".format(start_date, start_time)
  new_end = "{}:{}".format(end_date, end_time)

  return [new_start, new_end]
