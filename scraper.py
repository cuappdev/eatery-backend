from datetime import datetime, timedelta
from time import strptime

from bs4 import BeautifulSoup
import requests

BASE_URL = 'https://www.cornell.edu/academics/calendar/index.cfm?year='

"""
Scrape Cornell school breaks
Params:
  year_href: string representing the year such as "2018-2019"
Returns:
  dict of school breaks with their respective dates
"""
def scrape_breaks(year_href):
  result = {}
  year = year_href.split('-')
  page = requests.get(f'{BASE_URL}{year_href[:4]}-{year_href[7:]}').text
  soup = BeautifulSoup(page, 'lxml')
  tables = soup.findAll('table', {'class': 'cu-table'})

  for table in tables:
    if table.caption.text == f'Fall {year[0]}':
      parse_fall(table, result)
    elif table.caption.text == f'Spring {year[1]}':
      parse_spring(table, result)

  result['summer'] += f'-{get_last_day_summer(int(year[1]))}'

  return result

"""
Scrape Cornell breaks in the fall semester
Params:
  fall_table: HTML table containing all of the holidays in the fall semester
  dates: current dict containing the breaks to add to
"""
def parse_fall(fall_table, dates):
  year = int(fall_table.caption.text.split(' ')[1])
  rows = fall_table.tbody.find_all('tr')

  parsed_fall_break = False
  parsed_exams = False

  for row in rows:
    cols = row.findAll('td')
    date_str = cols[2].text.split(' ')
    month_num = convert_month(date_str[0])
    date = datetime(year, month_num, int(date_str[1]))

    if cols[0].text == 'Fall Break begins':
      dates['fall'] = date.strftime('%x')
    elif cols[0].text == 'Thanksgiving break begins':
      dates['thanksgiving'] = date.strftime('%x')
    elif cols[0].text == 'Instruction Resumes':
      # Gets last day of the break
      prev_day = date - timedelta(days=1)
      if not parsed_fall_break:
        parsed_fall_break = True
        dates['fall'] += f"-{prev_day.strftime('%x')}"
      else:
        dates['thanksgiving'] += f"-{prev_day.strftime('%x')}"
    elif cols[0].text == 'Study Period':
      dates['finals_winter'] = date.strftime('%x')
    elif cols[0].text == 'Scheduled Exams':
      if not parsed_exams:
        parsed_exams = True
        end_date = datetime(year, month_num, int(date_str[3]))
        dates['finals_winter'] += f"-{end_date.strftime('%x')}"
      else:
        end_date = date
        beginning_index = dates['finals_winter'].find('-')
        if beginning_index != -1:
          dates['finals_winter'] = dates['finals_winter'][:beginning_index] + f"-{end_date.strftime('%x')}"

      first_day_winter = end_date + timedelta(days=1)
      dates['winter'] = first_day_winter.strftime('%x')

"""
Scrape Cornell breaks in the spring semester
Params:
  spring_table: HTML table containing all of the holidays in the spring semester
  dates: current dict containing the breaks to add to
"""
def parse_spring(spring_table, dates):
  year = int(spring_table.caption.text.split(' ')[1])
  rows = spring_table.tbody.find_all('tr')

  parsed_feb_break = False

  for row in rows:
    cols = row.findAll('td')
    date_str = cols[2].text.split(' ')
    month_num = convert_month(date_str[0])
    date = datetime(year, month_num, int(date_str[1]))

    if cols[0].text == 'Instruction begins':
      last_day_winter = date - timedelta(days=1)
      dates['winter'] += f"-{last_day_winter.strftime('%x')}"
    elif cols[0].text == 'February Break begins':
      dates['february'] = date.strftime('%x')
    elif cols[0].text == 'Spring Break begins':
      dates['spring'] = date.strftime('%x')
    elif cols[0].text == 'Instruction Resumes':
      # Gets last day of the break
      prev_day = date - timedelta(days=1)
      if not parsed_feb_break:
        parsed_feb_break = True
        dates['february'] += f"-{prev_day.strftime('%x')}"
      else:
        dates['spring'] += f"-{prev_day.strftime('%x')}"
    elif cols[0].text == 'Study Period':
      dates['finals_spring'] = date.strftime('%x')
    elif cols[0].text == 'Scheduled Exams':
      end_date = datetime(year, month_num, int(date_str[3]))
      dates['finals_spring'] += f"-{end_date.strftime('%x')}"

      first_day_summer = end_date + timedelta(days=1)
      dates['summer'] = first_day_summer.strftime('%x')

"""
Gets the last day of summer by checking when the first day of classes is for the next year
Params:
  year: int representing the year
Returns:
  string representing the date of the last day of summer
"""
def get_last_day_summer(year):
  page = requests.get(f'{BASE_URL}{year}-{str(year + 1)[2:]}').text
  soup = BeautifulSoup(page, 'lxml')
  tables = soup.findAll('table', {'class': 'cu-table'})

  for table in tables:
    if table.caption.text == f'Fall {year}':
      rows = table.tbody.find_all('tr')
      for row in rows:
        cols = row.findAll('td')
        if cols[0].text == 'Instruction begins':
          date_str = cols[2].text.split(' ')
          month_num = convert_month(date_str[0])
          date = datetime(year, month_num, int(date_str[1])) - timedelta(days=1)
          return date.strftime('%x')

"""
Converts a month string to the corresponding number
Params:
  month_str: string representing the month such as "February"
Returns:
  int representing the month so convert_month("February") would return 2
"""
def convert_month(month_str):
  month_abbrv = month_str[:3]
  return strptime(month_abbrv, '%b').tm_mon

"""
Gets the current breaks
Returns:
  dict of school breaks and their respective dates
"""
def get_current_breaks():
  curr_year = datetime.now().year

  breaks = scrape_breaks(f'{curr_year - 1}-{curr_year}')
  last_day_summer = breaks['summer'].split('-')[1]

  if datetime.now() > datetime.strptime(last_day_summer, '%x'):
    breaks = scrape_breaks(f'{curr_year}-{curr_year + 1}')

  return breaks
