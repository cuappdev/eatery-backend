from datetime import datetime
from threading import Timer

import requests

from src.collegetown import collegetown_search
from src.eatery import (
    parse_eatery,
    parse_collegetown_eateries,
    parse_static_eateries
)
from src.constants import (
    CORNELL_DINING_URL,
    STATIC_EATERIES_URL,
    UPDATE_DELAY
)
from src.schema import Data
from src.swipes import export_data, parse_to_csv

campus_eateries = {}
collegetown_eateries = {}
all_swipe_data = {}

def start_update():
  """Starts the data retrieval process.

  Begins the process of getting data for the campus_eateries dictionary,
  from Cornell Dining and the static source, and collegetown_eateries dictionary,
  from Yelp.
  """
  try:
    global all_swipe_data
    print('[{}] Updating swipe data'.format(datetime.now()))
    data_path = parse_to_csv(file_name='data.csv')
    all_swipe_data = export_data(data_path)
    print('[{}] Updating campus'.format(datetime.now()))
    # Get data for on-campus, Cornell-owned dining Options
    dining_query = requests.get(CORNELL_DINING_URL)
    data_json = dining_query.json()
    parse_eatery(data_json, campus_eateries, all_swipe_data)
    merge_hours(campus_eateries)
    # Get data for on-campus, 3rd-party dining options
    static_json = requests.get(STATIC_EATERIES_URL).json()
    parse_static_eateries(static_json, campus_eateries, all_swipe_data)
    Data.update_data(campus_eateries)
    # Get data for Collegetown eateries
    # # print('[{}] Updating collegetown'.format(datetime.now()))
    # # yelp_query = collegetown_search()
    # # parse_collegetown_eateries(yelp_query, collegetown_eateries)
    # # Data.update_collegetown_data(collegetown_eateries)
    print('[{}] All data updated, waiting for requests'.format(datetime.now()))
  except Exception as e:
    print('Data update failed:', e)
  finally:
    Timer(UPDATE_DELAY, start_update).start()

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
        if (event.start_time == base_event.end_time and
            base_event.menu and
            (not event.menu or
            event.menu[0].equals(base_event.menu[0]))):
          base_event.end_time = event.end_time
          operating_hour.events.remove(event)
          print('merged events for {} on {}'.format(eatery.name, operating_hour.date))
        else:
          base_event = event
