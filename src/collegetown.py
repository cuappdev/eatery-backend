from os import environ
from time import sleep

from yelpapi import YelpAPI

from src.constants import YELP_LATITUDE, YELP_LONGITUDE, YELP_QUERY_DELAY, YELP_RADIUS, YELP_RESTAURANT_LIMIT

yelp_api = YelpAPI(environ.get("YELP_API_KEY"))


def collegetown_search():
    try:
        search = yelp_api.search_query(
            latitude=YELP_LATITUDE, limit=YELP_RESTAURANT_LIMIT, longitude=YELP_LONGITUDE, radius=YELP_RADIUS
        )
        eateries = []
        for place in search["businesses"]:
            eatery_id = place["id"]
            id_query = yelp_api.business_query(id=eatery_id)
            eateries.append(id_query)
            sleep(YELP_QUERY_DELAY)  # delay between query calls to not trigger yelp query limits
        print("Done with Collegetown Search")
        return eateries
    except Exception as e:
        print(e)
        return []
