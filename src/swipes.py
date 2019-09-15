from datetime import date, datetime, timedelta
from file_read_backwards import FileReadBackwards
import json
from os.path import isfile
import numpy as np
import pandas as pd

from src.constants import (
    BRB_ONLY,
    DINING_HALL,
    EATERY_DATA_PATH,
    LOCATION_NAMES,
    SCHOOL_BREAKS,
    SWIPE_DENSITY_ROUND,
    TABLE_COLUMNS,
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


def parse_to_csv(file_name="data.csv"):
    """Takes in a data.log file of swipe logs and converts them to a tabular format.
  Creates one csv file or updates file if one already exists:

  Keyword arguments:
  file_name -- the file name to use for the output csv file (default 'data.csv')

  Table columns:
  date -- date of the swipe event, string (mm/dd/yyyy)
  weekday -- weekday of swipe event, string (ex: 'monday', 'tuesday', etc.)
  in_session -- whether or not school is on a break, boolean
  location -- eatery of swipe event, string
  start_time -- left edge of timeblock, string (hh:mm)
  end_time -- right edge of timeblock, string (hh:mm)
  swipes -- number of swipes, int
  multiplier -- coefficient for converting average swipes/time into a wait time estimate, float
  """
    global breaks
    global weekdays
    main_csv = "{}{}".format(EATERY_DATA_PATH, file_name)

    try:
        with FileReadBackwards("{}{}".format(EATERY_DATA_PATH, "data.log")) as swipe_data:
            data_list = []
            update_info = {}

            # check if data csv file already exists
            if isfile(main_csv):
                try:
                    df = pd.read_csv(main_csv)
                    marker_row = df.head(1)
                    df.drop(marker_row.index, inplace=True)  # remove previous time marker
                    update_info["end"] = marker_row
                    update_info["old_data"] = df
                except:
                    print("failed in marker row creation")

            # read most recent data first
            for line in swipe_data:
                # skip over empty log lines
                if not line:
                    continue

                obj = json.loads(line)
                timestamp_str = obj.get("TIMESTAMP", None)
                if not timestamp_str:
                    # we have received {"msg":"Unauthorized"} as a log twice instead of real data
                    continue
                if timestamp_str == "Invalid date" or not obj["UNITS"]:  # obj['UNITS'] contains locations
                    continue

                if "new_marker" not in update_info:
                    # mark the timestamp to stop at on next update
                    update_info["new_marker"] = pd.DataFrame(
                        data={
                            "date": timestamp_str,
                            "end_time": "",
                            "session_type": "",
                            "location": "",
                            "start_time": "",
                            "swipes": 0,
                            "weekday": "",
                            "multiplier": 0,
                        },
                        index=[0],
                    )
                    print("new marker made")

                if "end" in update_info and update_info["end"].iloc[0]["date"] == timestamp_str:
                    print("hit time marker from last update on {}".format(timestamp_str))
                    break

                # timestamps strings typically end on a '00' representing fractions of a second but
                # occasionally end with a '01' as a rounding error on Cornell's side.
                # datetime.strptime crashes if the format does not perfectly match hence the checking
                if timestamp_str[-4] == "0":
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %I:%M:00 %p")
                elif timestamp_str[-4] == "1":
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %I:%M:01 %p")
                else:
                    continue

                date = timestamp.date()
                session_type = sort_session_type(date, breaks)
                weekday = weekdays[timestamp.weekday()]

                # sort time into a time block
                if timestamp.minute > 30:
                    delta = timedelta(minutes=30)
                    start_time = timestamp.strftime("%H:30")
                    end_time = (timestamp + delta).strftime("%H:00")
                elif timestamp.minute == 0:
                    delta = timedelta(minutes=1)
                    start_time = (timestamp - delta).strftime("%H:30")
                    end_time = timestamp.strftime("%H:00")
                elif timestamp.minute <= 30:
                    start_time = timestamp.strftime("%H:00")
                    end_time = timestamp.strftime("%H:30")

                for place in obj["UNITS"]:
                    location = place["UNIT_NAME"]
                    # remove locations that are not eateries we care about
                    if location not in LOCATION_NAMES:
                        continue
                    data_list.append(
                        pd.DataFrame(
                            data={
                                "date": timestamp.strftime("%m/%d/%Y"),
                                "end_time": end_time,
                                "session_type": session_type,
                                "location": location,
                                "start_time": start_time,
                                "swipes": place.get("CROWD_COUNT", 0),
                                "weekday": weekday,
                                "multiplier": WAIT_TIME_CONVERSION[LOCATION_NAMES[location]["type"]],
                            },
                            index=[0],
                        )
                    )

            print("done parsing data.log")

            if "old_data" in update_info:
                data_list.append(update_info["old_data"])
            df = pd.concat(data_list)
            df.to_csv(main_csv, header=True, index=False)
            data_file = sort_by_timeblock(main_csv)

            # add new marker to front of table to be used next time for time tracking
            df = pd.concat([update_info["new_marker"], df])
            df.to_csv(main_csv, header=True, index=False)
            return data_file

    except Exception as e:
        print("Failed at parse_to_csv")
        print("Data update failed:", e)


def sort_by_timeblock(input_file_path, output_file="timeblock-averages.csv"):
    """Sorts and runs average swipe/time calculations.
  Saves to a csv file or updates files if one already exists

  Keyword arguments:
  input_file_path -- the file path to our input csv file with all swipe logs, string
  output_file -- the file name for the output csv file (default 'timeblock-averages.csv')

  Table columns:
  session_type -- type of class session (regular, winter, summer, finals, etc.)
  weekday -- weekday of swipe event, string (ex: monday, tuesday, etc.)
  location -- eatery of swipe event, string (some locations have different names than dining.now's)
  start_time -- left edge of timeblock, string (hh:mm)
  end_time -- right edge of timeblock, string (hh:mm)
  swipes -- number of swipes, int
  counter -- number of events within this timeblock (used to calculate average), int
  average -- average number of swipes in this timeblock, float (2 decimals)
  multiplier -- coefficient for converting average swipes/time into a wait time estimate, float
  """
    try:
        all_but_swipes = list(TABLE_COLUMNS)
        all_but_swipes.remove("swipes")
        all_but_date = list(TABLE_COLUMNS)
        all_but_date.remove("date")
        all_but_date_and_swipes = list(all_but_date)
        all_but_date_and_swipes.remove("swipes")
        df = pd.read_csv(input_file_path)
        # sum together the swipes of rows with same timeblock/eatery makeup
        swipes_grouped = df.groupby(all_but_swipes).sum().reset_index()
        # count how many days of the same timeblock/eatery combo we have --> used for counter column
        dates_grouped = swipes_grouped.groupby(all_but_date).count().reset_index()
        counter_rename = dates_grouped.rename(index=str, columns={"date": "counter"})
        # sum together swipes and counters for rows with the same timeblock and location
        final_grouping = counter_rename.groupby(all_but_date_and_swipes).sum().reset_index()
        calculate_wait_times(final_grouping)
        final_grouping.sort_values(by=["location", "weekday"])
        output_path = "{}{}".format(EATERY_DATA_PATH, output_file)
        final_grouping.to_csv(output_path, header=True, index=False)
        return output_path
    except Exception as e:
        print("Failed at sort_by_timeblock")
        print("Data update failed:", e)


def sort_by_day(input_file_path, output_file="daily-averages.csv"):
    """Sorts and runs average swipe/time calculations.
  Saves to a csv file or updates files if one already exists
  Currently not used in main code, but allows for future use of data

  Keyword arguments:
  input_file_path -- the file path to our input csv file with all swipe logs, string
  output_file -- the file name for the output csv file (default 'daily-averages.csv')

  Table columns:
  weekday -- weekday of swipe event, string (ex: monday, tuesday, etc.)
  in_session -- whether or not school is on a break, boolean
  location -- eatery of swipe event, string (some locations have different names than dining.now's)
  swipes -- number of swipes, int
  counter -- number of events within this timeblock (used to calculate average), int
  average -- average number of swipes in this timeblock, float (2 decimals)
  """
    try:
        df = pd.read_csv(input_file_path)
        df = df.drop(columns=["start_time", "end_time", BRB_ONLY, DINING_HALL, TRILLIUM])
        # sum together the swipes of rows with same day/eatery makeup
        swipes_grouped = df.groupby(["date", "session_type", "weekday", "location"]).sum().reset_index()
        # count the number of times a location/date pair occur
        location_grouped = (
            swipes_grouped.groupby(["weekday", "location", "swipes", "session_type"]).count().reset_index()
        )
        counter_rename = location_grouped.rename(index=str, columns={"date": "counter"})
        # sum swipes and counters for rows with the same weekday and location
        final_grouping = counter_rename.groupby(["weekday", "location", "session_type"]).sum().reset_index()
        final_grouping["average"] = np.around(
            np.divide(final_grouping["swipes"], final_grouping["counter"]), decimals=2
        )
        final_grouping.sort_values(by=["location", "weekday"])
        final_grouping.to_csv("{}{}".format(EATERY_DATA_PATH, output_file), header=True, index=False)
    except Exception as e:
        print("Failed at sort_by_day")
        print("Data update failed:", e)


def export_data(file_path):
    """Transforms our tabular data into custom objects to be placed in Eatery objects

  Keyword arguments:
  file_path -- the file path to our input csv file with all wait time data, string
  """
    global breaks
    global weekdays

    try:
        df = pd.read_csv(file_path)
        data = {}
        today = date.today()
        session_type = sort_session_type(today, breaks)
        for location in df["location"].unique():
            eatery_name = LOCATION_NAMES[location]["name"]
            # look at information that pertains to today's criteria
            today_df = df.loc[(df["location"] == location) & (df["weekday"] == weekdays[today.weekday()])]

            if today_df.empty:
                print("{} has no swipe data for {}".format(eatery_name, weekdays[today.weekday()]))
                continue

            # df contains current session
            if today_df["session_type"].str.contains(session_type, regex=False).any():
                today_df = today_df.loc[(today_df["session_type"] == session_type)]
            else:  # not all breaks will be in data to start, default to regular for time being
                print("defaulting to regular session_type")
                today_df = today_df.loc[(today_df["session_type"] == "regular")]

            max_swipes = today_df["average"].max()
            json_data = json.loads(today_df.to_json(orient="table"))

            for row in json_data["data"]:
                new_timeblock = SwipeDataType(  # represents the data for a single timeblock of swipe data
                    end_time=row["end_time"],
                    session_type=session_type,
                    start_time=row["start_time"],
                    swipe_density=round(row["average"] / max_swipes, SWIPE_DENSITY_ROUND),
                    wait_time_high=row["wait_time_high"],
                    wait_time_low=row["wait_time_low"],
                )

                if eatery_name not in data:
                    data[eatery_name] = [new_timeblock]
                else:
                    data[eatery_name].append(new_timeblock)

        return data

    except Exception as e:
        print("Failed at export_data")
        print("Data update failed:", e)
        return {}


def aggregate_breaks(base_df):
    """Returns the dataframe with wait time calculations done on the combination of all break data.

  Keyword arguments:
  base_df -- the input dataframe which only contains one location and one day of the week

  NOTE: This method is currently not working as intended so it is not present in the live code.
  """
    all_but_date_and_swipes = list(TABLE_COLUMNS)
    all_but_date_and_swipes.remove("swipes")
    all_but_date_and_swipes.remove("date")
    df = base_df.copy(deep=True).drop(columns=["wait_time_low", "wait_time_high"])
    df = df.loc[(df["session_type"] != "regular")]
    df = df.groupby(all_but_date_and_swipes).sum().reset_index()
    return calculate_wait_times(df)


def calculate_wait_times(df):
    """Returns a df with calculated wait times given the swipe and counter columns

  Keyword arguments:
  df -- the input dataframe, already contains columns 'swipes' and 'counter'

  The input dataframe (df) should already have columns 'swipes' and 'counter'
  """
    df["average"] = np.around(np.divide(df["swipes"], df["counter"]), decimals=2)
    df["wait_time_low"] = np.floor(np.multiply(df["average"], df["multiplier"]))
    df["wait_time_high"] = np.ceil(np.multiply(df["average"], df["multiplier"]))
    df["wait_time_high"] = np.add(df["wait_time_high"], 2)  # expands bounds
    print("wait time calculations done")
    return df


def wait_time_multiply(df, type, multiplier):
    """Returns a new column which is the 'average' column times a cetain multiplier"""
    return np.multiply(df["average"], multiplier, where=df[type])


def sort_session_type(date, breaks):
    """Sorts the given date to the proper session_type

  Keyword arguments:
  date -- the current date we want to sort, datetime.date object
  breaks -- a dictionary containing all of the school breaks and their corresponding ranges
  """
    for label, dates in breaks.items():
        if dates[0] <= date <= dates[1]:
            return label
    return "regular"
