from datetime import date, datetime, timedelta
from threading import Timer

import requests

from src.collegetown import collegetown_search
from src.constants import (
    CORNELL_DINING_URL,
    IMAGES_URL,
    NUM_DAYS_STORED_IN_DB,
    PAY_METHODS,
    STATIC_EATERIES_URL,
    STATIC_MENUS_URL,
    TRILLIUM_ID,
    UPDATE_DELAY,
    WEEKDAYS,
)
from src.schema import Data
from src.types import (
    CampusAreaType,
    CampusEateryType,
    CollegetownEateryType,
    CollegetownEventType,
    CollegetownHoursType,
    CoordinatesType,
    EventType,
    FoodItemType,
    FoodStationType,
    OperatingHoursType,
    PaymentMethodsType,
)

campus_eateries = {}
collegetown_eateries = {}
static_eateries = {}

today = date.today()

def start_update():
  """Starts the data retrieval process.

  Begins the process of getting data for the campus_eateries dictionary,
  from Cornell Dining and the static source, and collegetown_eateries dictionary,
  from Yelp.
  """
  try:
    print('[{}] Updating campus'.format(datetime.now()))
    # Get data for on-campus, Cornell-owned dining Options
    dining_query = requests.get(CORNELL_DINING_URL)
    data_json = dining_query.json()
    parse_eatery(data_json)
    merge_hours(campus_eateries)
    # Get data for on-campus, 3rd-party dining options
    static_json = requests.get(STATIC_EATERIES_URL).json()
    parse_static_eateries(static_json)
    Data.update_data(campus_eateries)
    # Get data for Collegetown eateries
    print('[{}] Updating collegetown'.format(datetime.now()))
    yelp_query = collegetown_search()
    parse_collegetown_eateries(yelp_query)
    Data.update_collegetown_data(collegetown_eateries)
  except Exception as e:
    print('Data update failed:', e)
  finally:
    Timer(UPDATE_DELAY, start_update).start()

def parse_eatery(data_json):
  """Parses a Cornell Dining json dictionary.

  Fills the campus_eateries dictionary with objects of type CampusEateryType.

  Args:
      data_json (dict): a valid dictionary from the Cornell Dining json
  """
  for eatery in data_json['data']['eateries']:
    eatery_id = eatery.get('id', resolve_id(eatery))
    dining_items = get_trillium_menu() if eatery_id == TRILLIUM_ID else parse_dining_items(eatery)
    phone = eatery.get('contactPhone', 'N/A')
    phone = phone if phone else 'N/A'  # handle None values

    new_eatery = CampusEateryType(
        about=eatery.get('about', ''),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        eatery_type=parse_eatery_type(eatery),
        id=eatery_id,
        image_url=get_image_url(eatery.get('slug', '')),
        location=eatery.get('location', ''),
        name=eatery.get('name', ''),
        name_short=eatery.get('nameshort', ''),
        operating_hours=parse_operating_hours(eatery, dining_items),
        payment_methods=parse_payment_methods(eatery['payMethods']),
        phone=phone,
        slug=eatery.get('slug', '')
    )
    campus_eateries[new_eatery.id] = new_eatery

def get_image_url(slug):
  """Generates a URL for an image.

  Creates a string that represents a url pointing towards the eatery image.

  Args:
      slug (string): a slugged name of an eatery
  """
  return "{}{}.jpg".format(IMAGES_URL, slug)

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

def parse_operating_hours(eatery, dining_items):
  """Returns a list of OperatingHoursTypes for each dining event for an eatery.

  Calls parse_events to populate the events field for OperatingHoursType.

  Args:
      eatery (dict): A valid json segment from Cornell Dining that contains eatery information
      dining_items (list): A list that holds a dictionary for the items an eatery serves and a flag
       for healthy options
  """
  new_operating_hours = []
  hours_list = eatery['operatingHours']
  for hours in hours_list:
    new_date = hours.get('date', '')
    hours_events = hours['events']
    #merge the dining items from the json (for non-dining hall eateries) with the menu for an event
    for event in hours_events:
      if not event['menu'] and dining_items:
        event['menu'] = dining_items

    new_operating_hour = OperatingHoursType(
        date=new_date,
        events=parse_events(hours_events, new_date)
    )
    new_operating_hours.append(new_operating_hour)
  return new_operating_hours

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

def parse_campus_area(eatery):
  """Parses the common name location of an eatery.

  Returns a new CampusAreaType that contains a description of an eatery

  Args:
      eatery (dict): A valid json dictionary from Cornell Dining that contains eatery information
  """
  description, description_short = '', ''
  if 'campusArea' in eatery:
    description_short = eatery['campusArea']['descrshort']
  return CampusAreaType(
      description_short=description_short
  )

def parse_static_eateries(static_json):
  """Parses a static dining json dictionary.

  Similar to the parse_eatery function except for static source. Uses parse_static_op_hours to
  populate the operating_hours field in a CampusEateryType.

  Args:
      static_json (dict): A valid dictionary in the format of the dynamic Cornell Dining json for
        static eateries
  """
  for eatery in static_json['eateries']:
    new_eatery = CampusEateryType(
        about=eatery.get('about', ''),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        eatery_type=parse_eatery_type(eatery),
        id=eatery.get('id', resolve_id(eatery)),
        image_url=get_image_url(eatery.get('slug')),
        location=eatery.get('location', ''),
        name=eatery.get('name', ''),
        name_short=eatery.get('nameshort', ''),
        operating_hours=parse_static_op_hours(
            eatery.get('operatingHours', []),
            parse_dining_items(eatery),
            eatery.get('datesClosed', [])
        ),
        payment_methods=parse_payment_methods(eatery.get('payMethods', [])),
        phone=eatery.get('contactPhone', 'N/A'),
        slug=eatery.get('slug', '')
    )
    campus_eateries[new_eatery.id] = new_eatery

def resolve_id(eatery, collegetown=False):
  """Returns a new id (int) for an external eatery
  If the eatery does not have a provided id, we need to create one.
  Since all provided eatery ID values are positive, we decrement starting at 0.
  """
  if not collegetown and 'id' in eatery:
    return eatery['id']
  elif eatery['name'] in static_eateries:
    return static_eateries['id']

  static_eateries[eatery['name']] = -1 * len(static_eateries)
  return -1 * len(static_eateries)

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

def parse_static_op_hours(hours_list, dining_items, dates_closed):
  """Parses the hours of a static eatery.

  Returns a list with an OperatingHoursType, similar to parse_operating_hours, but includes
  checking for dates the eatery is closed.

  Args:
      hours_list (list): A list containing the days a static eatery is open
      dining_items (list): A list that holds a dictionary for the items an eatery serves and a flag
       for healthy options
      dates_closed (list): A list containg all the dates that an eatery is closed outside of its
        weekly schedule
  """
  weekdays = {}
  for hours in hours_list:
    if '-' in hours['weekday']:
      start, end = hours['weekday'].split('-')
      start_index = WEEKDAYS[start]
      end_index = WEEKDAYS[end] + 1
      days = list(range(start_index, end_index))
    else:
      days = [WEEKDAYS[hours['weekday']]]
    for weekday in days:
      if weekday not in weekdays:
        weekdays[weekday] = hours['events']

  new_operating_hours = []
  for i in range(NUM_DAYS_STORED_IN_DB):
    new_date = today + timedelta(days=i)
    for dates in dates_closed:
      if '-' not in dates:
        closed_date = datetime.strptime(dates, '%m/%d/%y').date()
        if new_date == closed_date:
          break
      else:
        start_str, end_str = dates.split('-')
        start_date = datetime.strptime(start_str, '%m/%d/%y').date()
        end_date = datetime.strptime(end_str, '%m/%d/%y').date()
        if start_date <= new_date <= end_date:
          break
    else:
      # new_date is not present in dates_closed, we can add this date to the db
      new_events = weekdays.get(new_date.weekday(), [])
      for event in new_events:
        event['menu'] = dining_items

      new_operating_hours.append(
          OperatingHoursType(
              date=new_date.isoformat(),
              events=parse_events(new_events, new_date.isoformat())
          )
      )
  return new_operating_hours

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

def get_trillium_menu():
  """Gets the Trillium menu.

  Returns the Trillium dining items (using parse_dining_items) from the static json source
  for menus.
  """
  static_json = requests.get(STATIC_MENUS_URL).json()
  return parse_dining_items(static_json['Trillium'][0])

def merge_hours(eateries):
   """Merges invalid events with valid events

   Combines events with no menu and a start_time equal to the end_time of a previous event into
   one event. This removes the effectively removes the events with no menus and only preserves
   the end time of the invalid event.

   Args:
       eateries (dict): A dictionary containing information provided from Cornell Dining and filled
         with CampusEateryTypes
   """
  for eatery in eateries.values():
    for operating_hour in eatery.operating_hours:
      if len(operating_hour.events) <= 1:  # ignore hours that don't have multiple events
        continue
      base_event = operating_hour.events[0]
      for event in operating_hour.events[1:]:  # iterate over copy of list so we can safely remove
        if event.start_time == base_event.end_time and \
            (not event.menu or event.menu[0].equals(base_event.menu[0])):
          base_event.end_time = event.end_time
          operating_hour.events.remove(event)
          print('merged events for {} on {}'.format(eatery.name, operating_hour.date))
        base_event = event

def parse_collegetown_eateries(collegetown_data):
  """Parses Collegetown json dictionary.

  Fills the collegetown_eateries list with objects of type CollegetownEateryType.

  Args:
      collegetown_data (dict): A valid json dictionary from Yelp that contains eatery information
  """
  for eatery in collegetown_data:
    new_id = resolve_id(eatery, collegetown=True)
    new_eatery = CollegetownEateryType(
        address=eatery['location']['address1'],
        categories=[cuisine['title'] for cuisine in eatery.get('categories', [])],
        coordinates=parse_coordinates(eatery),
        eatery_type='Collegetown Restaurant',
        id=new_id,
        image_url=eatery.get('image_url', ''),
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
        phone=eatery.get('phone', 'N/A'),
        price=eatery.get('price', ''),
        rating=eatery.get('rating', 'N/A'),
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
