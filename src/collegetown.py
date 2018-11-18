from os import environ
from time import sleep

from pprint import pprint
from yelpapi import YelpAPI

from src.constants import (
    YELP_LATITUDE,
    YELP_LONGITUDE,
    YELP_RADIUS,
    YELP_NUMBER_LIMIT,
    YELP_QUERY_DELAY,
)

API_KEY = environ.get('YELP_API_KEY')

yelp_api = YelpAPI(API_KEY)

def yelp_search(text, latitude=YELP_LATITUDE, longitude=YELP_LONGITUDE):
  try:
    print('searching..')
    search = yelp_api.search_query(term=text, longitude=longitude, latitude=latitude, limit=5)
    eatery = search['businesses'][0]
    eatery_id = eatery['id']
    id_query = yelp_api.business_query(id=eatery_id)
    pprint(id_query)
  except Exception as e:
    print('something went wrong: ' + e)

def collegetown_search():
  try:
    search = yelp_api.search_query(
        longitude=YELP_LONGITUDE,
        latitude=YELP_LATITUDE,
        radius=YELP_RADIUS,
        limit=YELP_NUMBER_LIMIT
    )
    # print(len(search['businesses']))  #yelp will return at most 50
    eateries = []
    for place in search['businesses']:
      eatery_id = place['id']
      id_query = yelp_api.business_query(id=eatery_id)
      # pprint(id_query)
      eateries.append(id_query)
      sleep(YELP_QUERY_DELAY)  # delay between query calls to not trigger yelp query limits
    return eateries
  except Exception as e:
    print(e)
