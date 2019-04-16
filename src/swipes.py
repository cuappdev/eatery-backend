from datetime import date, datetime, timedelta
import json
from os.path import isfile
import numpy as np
import pandas as pd

from src.constants import (
  BRB_ONLY,
  DINING_HALL,
  EATERY_DATA_PATH,
  LOCATION_NAMES,
  ISOLATE_COUNTER_SWIPES,
  ISOLATE_DATE,
  ISOLATE_SWIPES,
  SCHOOL_BREAKS,
  SWIPE_DENSITY_ROUND,
  TRILLIUM,
  WAIT_TIME_CONVERSION,
  WEEKDAYS,
)
from src.eatery import string_to_date_range
from src.types import SwipeDataType

weekdays = {v: k for k, v in WEEKDAYS.items()}  # inverting to convert strings to indexes [0,6]
breaks = {}
for label, dates in SCHOOL_BREAKS.items():
  breaks[label] = string_to_date_range(dates)

def parse_to_csv(file_name='data.csv'):
  """
  Takes in a data.log file of swipe logs and converts them to a tabular format.
  Argument limit: used to limit number of logs to parse (for testing purposes).
  Creates one csv file (updates file if already exists):
  data.csv - stores all swipe events
    date: date of swipe event, string (mm/dd/yyyy)
    weekday: weekday of swipe event, string (ex: monday, tuesday, etc.)
    in_session: whether or not school is on a break, boolean
    location: eatery of swipe event, string (some locations have different names than dining.now's)
    start_time: left edge of timeblock, string (hh:mm AM/PM)
    end_time: right edge of timeblock, string (hh:mm AM/PM)
    swipes: number of swipes, int
    brb_only: indicates if this location is a brb only eatery (used for calcs), boolean
    dining_hall: indicates if a location is a dining hall (used for calcs), boolean
    trillium: indicates if a location is Trillium (used for calcs), boolean
  """
  global breaks
  global weekdays
  main_csv = '{}{}'.format(EATERY_DATA_PATH, file_name)
  try:
    with open('{}{}'.format(EATERY_DATA_PATH, 'data.log'), 'r') as swipe_data:
      line_index = 0
      data_list = []
      update_info = {}

      # check if data csv file already exists
      if isfile(main_csv):
        try:
          df = pd.read_csv(main_csv)
          marker_row = df.head(1)
          print(marker_row.iloc[0]['date'])
          df.drop(marker_row.index, inplace=True)  # remove previous time marker
          update_info['end'] = marker_row
          update_info['old_data'] = df
        except Exception as e:
          print('failed in marker row creation')

      # read most recent data first
      for line in list(reversed(swipe_data.readlines())):
        # skip over empty log lines (odd lines going forward, even lines going reversed)
        if line_index % 2 == 0 or line == '\n':
          line_index += 1
          continue

        obj = json.loads(line)
        timestamp_str = obj['TIMESTAMP']
        if timestamp_str == 'Invalid date' or not obj['UNITS']:  # obj['UNITS'] contains locations
          line_index += 1
          continue

        if 'new_marker' not in update_info:
          # mark the timestamp to stop at on next update
          update_info['new_marker'] = pd.DataFrame(data={
              'date': timestamp_str,
              'end_time': '',
              'session_type': '',
              'location': '',
              'start_time': '',
              'swipes': 0,
              'weekday': '',
              BRB_ONLY: False,
              DINING_HALL: False,
              TRILLIUM: False,
          }, index=[0])
          print('new marker made')

        if 'end' in update_info and update_info['end'].iloc[0]['date'] == timestamp_str:
          print('hit time marker from last update on {}'.format(timestamp_str))
          break

        try:
          try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %I:%M:00 %p')
          except:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %I:%M:01 %p')
        except:
          continue

        date = timestamp.date()
        session_type = sort_session_type(date, breaks)
        weekday = weekdays[timestamp.weekday()]
        # sort time into a time block
        if timestamp.minute > 30:
          delta = timedelta(minutes=30)
          start_time = timestamp.strftime('%I:30 %p')
          end_time = (timestamp + delta).strftime('%I:00 %p')
        elif timestamp.minute == 0:
          delta = timedelta(minutes=1)
          start_time = (timestamp - delta).strftime('%I:30 %p')
          end_time = timestamp.strftime('%I:00 %p')
        elif timestamp.minute <= 30:
          start_time = timestamp.strftime('%I:00 %p')
          end_time = timestamp.strftime('%I:30 %p')

        for place in obj['UNITS']:
          location = place['UNIT_NAME']
          # remove locations that are not eateries we care about
          if location not in LOCATION_NAMES:
            continue
          data_list.append(pd.DataFrame(data={
              'date': timestamp.strftime('%m/%d/%Y'),
              'end_time': end_time,
              'session_type': session_type,
              'location': location,
              'start_time': start_time,
              'swipes': place['CROWD_COUNT'],
              'weekday': weekday,
              BRB_ONLY: True if LOCATION_NAMES[location]['type'] == BRB_ONLY else False,
              DINING_HALL: True if LOCATION_NAMES[location]['type'] == DINING_HALL else False,
              TRILLIUM: True if LOCATION_NAMES[location]['type'] == TRILLIUM else False,
              }, index=[0]))

        line_index += 1

      print('done parsing data.log')

      if 'old_data' in update_info:
        data_list.append(update_info['old_data'])
      df = pd.concat(data_list)
      df.to_csv(main_csv, header=True, index=False)
      data_file = sort_by_timeblock(main_csv)

      # add new marker to front of table to be used next time for time tracking
      df = pd.concat([update_info['new_marker'], df])
      df.to_csv(main_csv, header=True, index=False)
      return data_file

  except Exception as e:
    print('Failed at parse_to_csv')
    print('Data update failed:', e)

def sort_by_timeblock(input_file_path, output_file='timeblock-averages.csv'):
  """
  Sorts and runs average swipe/time calculations.
  Saves to a csv file (updates files if already exists):
  tb-averages.csv - the timeblock swipe averages
    session_type: type of class session (regular, winter, summer, finals, etc.)
    weekday: weekday of swipe event, string (ex: monday, tuesday, etc.)
    location: eatery of swipe event, string (some locations have different names than dining.now's)
    start_time: left edge of timeblock, string (hh:mm AM/PM)
    end_time: right edge of timeblock, string (hh:mm AM/PM)
    swipes: number of swipes, int
    counter: number of events within this timeblock (used to calculate average), int
    average: average number of swipes in this timeblock, float (2 decimals)
    brb_only: indicates if this location is a brb only eatery (used for calcs), boolean
    dining_hall: indicates if a location is a dining hall (used for calcs), boolean
    trillium: indicates if a location is Trillium (used for calcs), boolean
  """
  try:
    df = pd.read_csv(input_file_path)
    # sum together the swipes of rows with same timeblock/eatery makeup
    df = df.groupby(ISOLATE_SWIPES).sum().reset_index()
    # count how many days of the same timeblock/eatery combo we have --> used for counter column
    df = df.groupby(ISOLATE_DATE).count().reset_index()
    df = df.rename(index=str, columns={'date': 'counter'})
    # sum together swipes and counters for rows with the same timeblock and location
    df = df.groupby(ISOLATE_COUNTER_SWIPES).sum().reset_index()
    df = calculate_wait_times(df)
    df = df.sort_values(by=['location', 'weekday'])
    output_path = '{}{}'.format(EATERY_DATA_PATH, output_file)
    df.to_csv(output_path, header=True, index=False)
    return output_path
  except Exception as e:
    print('Failed at sort_by_timeblock')
    print('Data update failed:', e)


def sort_by_day(input_file_path, output_file='daily-averages.csv'):
  """
  Sorts and runs average swipe/time calculations.
  Saves to a csv file.  Currently not used in main code, but allows for future use of data
  daily-averages.csv - the daily swipe averages
    weekday: weekday of swipe event, string (ex: monday, tuesday, etc.)
    in_session: whether or not school is on a break, boolean
    location: eatery of swipe event, string (some locations have different names than dining.now's)
    swipes: number of swipes, int
    counter: number of events within this timeblock (used to calculate average), int
    average: average number of swipes in this timeblock, float (2 decimals)
  """
  try:
    df = pd.read_csv(input_file_path)
    df = df.drop(columns=['start_time', 'end_time', BRB_ONLY, DINING_HALL, TRILLIUM])
    # sum together the swipes of rows with same day/eatery makeup
    df = df.groupby(['date', 'session_type', 'weekday', 'location']).sum().reset_index()
    # count the number of times a location/date pair occur
    df = df.groupby(['weekday', 'location', 'swipes', 'session_type']).count().reset_index()
    df = df.rename(index=str, columns={'date': 'counter'})
    # sum swipes and counters for rows with the same weekday and location
    df = df.groupby(['weekday', 'location', 'session_type']).sum().reset_index()
    df['average'] = np.around(np.divide(df['swipes'], df['counter']), decimals=2)
    df = df.sort_values(by=['location', 'weekday'])
    df.to_csv('{}{}'.format(EATERY_DATA_PATH, output_file), header=True, index=False)
  except Exception as e:
    print('Faled at sort_by_day')
    print('Data update failed:', e)


def export_data(file_path):
  """
  Transforms our tabular data into custom objects to be placed in Eatery objects
  """
  global breaks
  global weekdays

  try:
    df = pd.read_csv(file_path)
    data = {}
    today = date.today()
    session_type = sort_session_type(today, breaks)

    for location in df['location'].unique():
      eatery_name = LOCATION_NAMES[location]['name']

      # look at information that pertains to today's criteria
      new_df = df.loc[(df['location'] == location) & (df['weekday'] == weekdays[today.weekday()])]

      # df contains current session
      if new_df['session_type'].str.contains(session_type, regex=False).any():
        new_df = new_df.loc[(new_df['session_type'] == session_type)]
      else:  # not all breaks will be in data to start, default to regular for time being
        print('defaulting to regular session_type')
        new_df = new_df.loc[(new_df['session_type'] == 'regular')]
        # new_df = aggregate_breaks(new_df)

      max_swipes = new_df['average'].max()
      json_data = json.loads(new_df.to_json(orient='table'))

      for row in json_data['data']:
        new_timeblock = SwipeDataType(  # represents the data for a single timeblock of swipe data
            end_time=row['end_time'],
            session_type=session_type,
            start_time=row['start_time'],
            swipe_density=round(row['average'] / max_swipes, SWIPE_DENSITY_ROUND),
            wait_time_high=row['wait_time_high'],
            wait_time_low=row['wait_time_low'],
        )

        if eatery_name not in data:
          data[eatery_name] = [new_timeblock]
        else:
          data[eatery_name].append(new_timeblock)

    return data

  except Exception as e:
    print('Failed at export_data')
    print('Data update failed:', e)
    return {}

def aggregate_breaks(base_df):
  """Returns the dataframe with wait time calculations done on the combination of all break data.
  The input dataframe (df) is already sorted to only contain a single location and day of the week.
  NOTE: This method is currently not working as intended so it is not present in the live code.
  """
  df = base_df.copy(deep=True).drop(columns=['wait_time_low', 'wait_time_high'])
  df = df.loc[(df['session_type'] != 'regular')]
  df = df.groupby(ISOLATE_COUNTER_SWIPES).sum().reset_index()
  return calculate_wait_times(df)

def calculate_wait_times(df):
  """Returns a df with calculated wait times given the swipe and counter columns
  The input dataframe (df) should already have columns 'swipes' and 'counter'.
  """
  df['average'] = np.around(np.divide(df['swipes'], df['counter']), decimals=2)
  for type, multiplier in WAIT_TIME_CONVERSION.items():
    df['wait_time_low'] = wait_time_multiply(df, type, multiplier)
    df['wait_time_high'] = wait_time_multiply(df, type, multiplier)
  df['wait_time_low'] = np.floor(df['wait_time_low'])
  df['wait_time_high'] = np.ceil(df['wait_time_high'])
  df['wait_time_high'] = np.add(df['wait_time_high'], 2)  # expands bounds
  print('wait time calculations done')
  return df

def wait_time_multiply(df, type, multiplier):
  return np.multiply(df['average'], multiplier, where=df[type])

def sort_session_type(date, breaks):
  """
  sorts the given date to the proper session_type
  """
  for label, dates in breaks.items():
    if dates[0] <= date <= dates[1]:
      return label
  return 'regular'
