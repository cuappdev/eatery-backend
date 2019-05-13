from os import environ
from time import sleep

from yelpapi import YelpAPI

from src.constants import (
    SWEETSPOT_ID,
    YELP_LATITUDE,
    YELP_LONGITUDE,
    YELP_QUERY_DELAY,
    YELP_RADIUS,
    YELP_RESTAURANT_LIMIT,
)

yelp_api = YelpAPI(environ.get('YELP_API_KEY'))

def collegetown_search():
  try:
    search = yelp_api.search_query(
        latitude=YELP_LATITUDE,
        limit=YELP_RESTAURANT_LIMIT,
        longitude=YELP_LONGITUDE,
        radius=YELP_RADIUS
    )
  except Exception as e:
    print('failed at yelp radial search')
    print(e)
    return []

  eateries = []
  for place in search.get('businesses', []):
    eatery_id = place['id']
    if eatery_id == SWEETSPOT_ID:
      continue
    try:
      id_query = yelp_api.business_query(id=eatery_id)
    except Exception as e:
      print('failed at business query with id {}'.format(eatery_id))
      print(e)
      continue
    eateries.append(id_query)
    sleep(YELP_QUERY_DELAY)  # delay between query calls to not trigger yelp query limits
  print('Done with Collegetown Search')
  return eateries
