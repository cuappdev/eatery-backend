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
  try:
    print('[{0}] Updating data'.format(datetime.now()))
    dining_query = requests.get(CORNELL_DINING_URL)
    data_json = dining_query.json()
    parse_eatery(data_json)
    statics_json = requests.get(STATIC_EATERIES_URL).json()
    parse_static_eateries(statics_json)
    yelp_query = collegetown_search()
    parse_collegetown_eateries(yelp_query)
    Data.update_data(campus_eateries, collegetown_eateries)
  except Exception as e:
    print('Data update failed:', e)
  finally:
    Timer(UPDATE_DELAY, start_update).start()

def parse_eatery(data_json):
  for eatery in data_json['data']['eateries']:
    eatery_id = eatery.get('id', resolve_id(eatery))
    dining_items = get_trillium_menu() if eatery_id == TRILLIUM_ID else parse_dining_items(eatery)
    phone = eatery.get('contactPhone', 'N/A')
    phone = phone if phone else 'N/A'  # handle None values

    new_eatery = CampusEateryType(
        about=eatery.get('about', ''),
        about_short=eatery.get('aboutshort', ''),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        eatery_type=parse_eatery_type(eatery),
        id=eatery_id,
        image_url=get_image_url(eatery.get('slug')),
        location=eatery.get('location', ''),
        name=eatery.get('name', ''),
        name_short=eatery.get('nameshort', ''),
        operating_hours=parse_operating_hours(eatery, eatery_id, dining_items),
        payment_methods=parse_payment_methods(eatery['payMethods']),
        phone=phone,
        slug=eatery.get('slug')
    )
    campus_eateries[new_eatery.id] = new_eatery

def get_image_url(slug):
  return "{}{}.jpg".format(IMAGES_URL, slug)

def parse_payment_methods(methods):
  payment_methods = PaymentMethodsType()
  payment_methods.brbs = any(pay['descrshort'] == PAY_METHODS['brbs'] for pay in methods)
  payment_methods.cash = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.credit = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.cornell_card = any(pay['descrshort'] == PAY_METHODS['c-card'] for pay in methods)
  payment_methods.mobile = any(pay['descrshort'] == PAY_METHODS['mobile'] for pay in methods)
  payment_methods.swipes = any(pay['descrshort'] == PAY_METHODS['swipes'] for pay in methods)
  return payment_methods

def parse_operating_hours(eatery, eatery_id, dining_items):
  new_operating_hours = []
  hours_list = eatery['operatingHours']
  for hours in hours_list:
    new_date = hours.get('date', '')
    hours_events = hours['events']

    for event in hours_events:
      if not event['menu'] and dining_items:
        event['menu'] = dining_items

    new_operating_hour = OperatingHoursType(
        date=new_date,
        events=parse_events(hours_events, eatery_id, new_date),
        status=hours.get('status', '')
    )
    new_operating_hours.append(new_operating_hour)
  return new_operating_hours

def parse_events(event_list, eatery_id, event_date):
  new_events = []
  for event in event_list:
    start, end = format_time(event.get('start', ''), event.get('end', ''), event_date)
    stations = parse_food_stations(event['menu'], eatery_id)
    new_event = EventType(
        cal_summary=event.get('calSummary', ''),
        description=event.get('descr', ''),
        end_time=end,
        menu=stations,
        start_time=start,
        station_count=len(stations)
    )
    new_events.append(new_event)
  return new_events

def parse_food_stations(station_list, eatery_id):
  new_stations = []
  for station in station_list:
    default_index = len(new_stations)
    station_items = parse_food_items(station['items'])
    new_station = FoodStationType(
        category=station.get('category', ''),
        items=station_items,
        item_count=len(station_items),
        sort_idx=station.get('sortIdx', default_index)
    )
    new_stations.append(new_station)
  return new_stations

def parse_food_items(item_list):
  new_food_items = []
  for item in item_list:
    default_index = len(new_food_items)
    new_food_items.append(
        FoodItemType(
            healthy=item.get('healthy', False),
            item=item.get('item', ''),
            sort_idx=item.get('sortIdx', default_index)
        )
    )
  return new_food_items

def parse_dining_items(eatery):
  dining_items = {'items': []}
  for item in eatery['diningItems']:
    default_index = len(dining_items['items'])
    dining_items['items'].append({
        'healthy': item.get('healthy', False),
        'item': item.get('item', ''),
        'sortIdx': item.get('sortIdx', default_index)
    })
  return [dining_items]

def parse_coordinates(eatery):
  latitude, longitude = 0.0, 0.0
  if 'coordinates' in eatery:
    latitude = eatery['coordinates']['latitude']
    longitude = eatery['coordinates']['longitude']
  return CoordinatesType(
      latitude=latitude,
      longitude=longitude,
  )

def parse_campus_area(eatery):
  description, description_short = '', ''
  if 'campusArea' in eatery:
    description = eatery['campusArea']['descr']
    description_short = eatery['campusArea']['descrshort']
  return CampusAreaType(
      description=description,
      description_short=description_short
  )

def parse_static_eateries(statics_json):
  for eatery in statics_json['eateries']:
    new_id = eatery.get('id', resolve_id(eatery))
    dining_items = parse_dining_items(eatery)
    new_eatery = CampusEateryType(
        about=eatery.get('about', ''),
        about_short=eatery.get('aboutshort', ''),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        eatery_type=parse_eatery_type(eatery),
        id=new_id,
        image_url=get_image_url(eatery.get('slug')),
        location=eatery.get('location', ''),
        name=eatery.get('name', ''),
        name_short=eatery.get('nameshort', ''),
        operating_hours=parse_static_op_hours(eatery['operatingHours'], new_id, dining_items),
        payment_methods=parse_payment_methods(eatery['payMethods']),
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
  try:
    return eatery['eateryTypes'][0]['descr']
  except Exception:
    return 'Unknown'

def parse_static_op_hours(hours_list, eatery_id, dining_items):
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
    new_events = weekdays.get(new_date.weekday(), [])

    for event in new_events:
      event['menu'] = dining_items

    new_operating_hours.append(
        OperatingHoursType(
            date=new_date.isoformat(),
            events=parse_events(new_events, eatery_id, new_date.isoformat()),
            status='EVENTS'
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
  statics_json = requests.get(STATIC_MENUS_URL).json()
  return parse_dining_items(statics_json['Trillium'][0])

def parse_collegetown_eateries(collegetown_data):
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
