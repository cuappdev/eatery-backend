from datetime import datetime, timedelta

from src.constants import (
    NUM_DAYS_STORED_IN_DB,
    WEEKDAYS
)
from src.eatery.common_eatery import (
    get_image_url,
    parse_campus_area,
    parse_coordinates,
    parse_dining_items,
    parse_eatery_type,
    parse_events,
    parse_payment_methods,
    parse_payment_methods_enum,
    resolve_id,
    today,
)
from src.types import (
    CampusEateryType,
    OperatingHoursType,
)

def parse_static_eateries(static_json, campus_eateries, all_swipe_data):
  """Parses a static dining json dictionary.

  Similar to the parse_eatery function except for static source. Uses parse_static_op_hours to
  populate the operating_hours field in a CampusEateryType.

  Args:
      static_json (dict): A valid dictionary in the format of the dynamic Cornell Dining json for
        static eateries
      campus_eateries (dict): A dictionary to fill with static eateries
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
        payment_methods_enums=parse_payment_methods_enum(eatery.get('payMethods', [])),
        phone=eatery.get('contactPhone', 'N/A'),
        slug=eatery.get('slug', ''),
        swipe_data=all_swipe_data.get(eatery.get('name', ''), [])
    )
    campus_eateries[new_eatery.id] = new_eatery

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
        start_date, end_date = string_to_date_range(dates)
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

def string_to_date_range(dates):
  """
  date: string representing a range of dates mm/dd/yy-mm/dd/yy
  """
  start_str, end_str = dates.split('-')
  start_date = datetime.strptime(start_str, '%m/%d/%y').date()
  end_date = datetime.strptime(end_str, '%m/%d/%y').date()
  return [start_date, end_date]
