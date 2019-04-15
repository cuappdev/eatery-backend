from os.path import isfile
from datetime import date, datetime, timedelta
import json
import numpy as np
import pandas as pd

from src.constants import (
  BRB_ONLY,
  DINING_HALL,
  EATERY_DATA_PATH,
  LOCATION_NAMES,
  SCHOOL_BREAKS,
  ISOLATE_COUNTER_SWIPES,
  ISOLATE_DATE,
  ISOLATE_SWIPES,
  WAIT_TIME_CONVERSION,
  WEEKDAYS,
)
from src.eatery import string_to_date_range
from src.types import SwipeDataType

weekdays = {index: day for day, index in WEEKDAYS.items()} # invert our weekday -> index dict
breaks = {}
for label, dates in SCHOOL_BREAKS.items():
  breaks[label] = string_to_date_range(dates)

def parse_to_csv(file_name='data.csv', limit=-1):
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
  """
  global breaks
  global weekdays
  MAIN_CSV = '{}{}'.format(EATERY_DATA_PATH, file_name)
  try:
    with open('{}{}'.format(EATERY_DATA_PATH, 'data.log'), 'r') as swipe_data:
      i = 0
      line_counter = 0
      data_list = []
      update_info = {}

      # check if data csv file already exists
      if isfile(MAIN_CSV):
        df = pd.read_csv(MAIN_CSV)
        marker_row = df.head(1)
        update_info['end'] = marker_row
        print(marker_row.iloc[0]['date'])
        df.drop(marker_row.index, inplace=True)  # remove previous time marker
        update_info['old_data'] = df
        print('marker and old data found')

      # read most recent data first
      for line in list(reversed(swipe_data.readlines())):
        if line_counter == limit:  # limit used for testing purposes
          break
        # skip over empty log lines (odd lines going forward, even lines goind reversed)
        if i % 2 == 0 or line == '\n':
          i += 1
          continue
        obj = json.loads(line)
        timestamp_str = obj['TIMESTAMP']
        if timestamp_str == 'Invalid date' or obj['UNITS'] == []:
          i += 1
          line_counter += 1
          continue
        if 'new_marker' not in update_info:
          # mark the timeblock to stop at on next update
          update_info['new_marker'] = pd.DataFrame(data={
              'date': timestamp_str,
              'end_time': '',
              'session_type': '',
              'location': '',
              'start_time': '',
              'swipes': 0,
              'weekday': '',
              'brb_only': False,
              'dining_hall': False,
              }, index=[0])
          print('new marker made')
        if 'end' in update_info and update_info['end'].iloc[0]['date'] == timestamp_str:
          print('hit time marker from last update on {}'.format(timestamp_str))
          break

        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %I:%M:00 %p')
        date = timestamp.date()
        # print(timestamp_str)
        session_type = sort_session_type(date, breaks)
        weekday = weekdays[timestamp.weekday()]
        # sort time into a time block
        if timestamp.minute > 30:
          delta = timedelta(minutes=30)
          start_time = timestamp.strftime('%I:30 %p')
          end_time = (timestamp+delta).strftime('%I:00 %p')
        elif timestamp.minute == 0:
          delta = timedelta(minutes=1)
          start_time = (timestamp-delta).strftime('%I:30 %p')
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
              'brb_only': False if LOCATION_NAMES[location]['type'] == DINING_HALL else True,
              'dining_hall': True if LOCATION_NAMES[location]['type'] == DINING_HALL else False,
              }, index=[0]))
        i += 1
        line_counter += 1
        # print('line done')

      print('done parsing data.log')
      if 'old_data' in update_info:
        data_list.append(update_info['old_data'])
      df = pd.concat(data_list)
      df.to_csv(MAIN_CSV, header=True, index=False)
      data_file = sort_by_timeblock(MAIN_CSV)
      # add new marker to front of table to be used next time for time tracking
      df = pd.concat([update_info['new_marker'], df])
      df.to_csv(MAIN_CSV, header=True, index=False)
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
  """
  try:
    df = pd.read_csv(input_file_path)
    # make copy
    # df_timeblock = df.copy(deep=True)
    # sum together the swipes of rows with same timeblock/eatery makeup
    df = df.groupby(ISOLATE_SWIPES).sum().reset_index()
    # count how many days of the same timeblock/eatery combo we have --> used for counter column
    df = df.groupby(ISOLATE_DATE).count().reset_index()
    df = df.rename(index=str, columns={'date': 'counter'})
    # sum together swipes and counters for rows with the same timeblock and location
    df = df.groupby(ISOLATE_COUNTER_SWIPES).sum().reset_index()
    df = calculate_wait_times(df)
    df = df.sort_values(by=['session_type', 'location', 'weekday'])
    output_path = '{}{}'.format(EATERY_DATA_PATH, output_file)
    df.to_csv(output_path, header=True, index=False)
    return output_path
  except Exception as e:
    print('Failed at sort_by_timeblock')
    print('Data update failed:', e)
    return None


def sort_by_day(input_file_path, output_file = 'daily-averages.csv'):
  """
  Sorts and runs average swipe/time calculations.
  Saves to a csv file (updates files if already exists):
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
    df = df.drop(columns=['start_time', 'end_time', 'dining_hall', 'brb_only'])
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
    session_type = 'spring'#sort_session_type(today, breaks)
    for location in df['location'].unique():
      true_location = LOCATION_NAMES[location]['name']
      # look at information that pertains to today's criteria
      new_df = df.loc[(df['location'] == location) & (df['weekday'] == weekdays[today.weekday()])]
      if df['session_type'].str.contains(session_type, regex=False).any():  # current session in df
        new_df = new_df.loc[(df['session_type'] == session_type)]
      else:  # not all breaks will be in data to start, average known break data as best estimate
        new_df = aggregate_breaks(new_df)
      max_swipes = new_df['average'].max()
      json_data = json.loads(new_df.to_json(orient='table'))
      for row in json_data['data']:
        new_timeblock = SwipeDataType(
            end_time=row['end_time'],
            session_type=session_type,
            start_time=row['start_time'],
            swipe_density=round(row['average']/max_swipes, 3),
            wait_time_high=row['wait_time_high'],
            wait_time_low=row['wait_time_low'],
        )
        if true_location not in data:
          data[true_location] = [new_timeblock]
        else:
          data[true_location].append(new_timeblock)
    return data
  except Exception as e:
    print('Failed at export_data')
    print('Data update failed:', e)
    return {}

def aggregate_breaks(base_df):
  # CURRENTLY NOT WORKING!!
  print('in aggregate_breaks')
  df = base_df.copy(deep=True).drop(columns=['wait_time_low', 'wait_time_high'])
  df = df.loc[(df['session_type'] != 'regular')]
  print(df)
  # df = df.drop(columns=['session_type'])
  df = df.groupby(ISOLATE_COUNTER_SWIPES).sum().reset_index()
  print('post grouping')
  return calculate_wait_times(df)

def calculate_wait_times(df):
  df['average'] = np.around(np.divide(df['swipes'], df['counter']), decimals=2)
  df['wait_time_low'] = np.floor(np.multiply(df['average'], WAIT_TIME_CONVERSION[BRB_ONLY], where=df[BRB_ONLY]))
  df['wait_time_low'] = np.floor(np.multiply(df['average'], WAIT_TIME_CONVERSION[DINING_HALL], where=df[DINING_HALL]))
  df['wait_time_high'] = np.ceil(np.multiply(df['average'], WAIT_TIME_CONVERSION[BRB_ONLY], where=df[BRB_ONLY]))
  df['wait_time_high'] = np.ceil(np.multiply(df['average'], WAIT_TIME_CONVERSION[DINING_HALL], where=df[DINING_HALL]))
  df['wait_time_high'] = np.add(df['wait_time_high'], 2)  # expand bounds
  print('wait time calcs done')
  return df

def sort_session_type(date, breaks):
  """
  sorts the given date to the proper session_type
  """
  for label, dates in breaks.items():
    if dates[0] <= date <= dates[1]:
      # print(label)
      return label
  return 'regular'
