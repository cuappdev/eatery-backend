import requests

from collegetown import collegetown_search
from constants import CORNELL_DINING_URL
from database import Base, Engine, Session
from eatery_db import parse_campus_eateries, parse_collegetown_eateries


def start_update():
    # try:
    Base.metadata.drop_all(bind=Engine)
    Base.metadata.create_all(bind=Engine)

    dining_query = requests.get(CORNELL_DINING_URL)
    data_json = dining_query.json()
    campus_eateries = parse_campus_eateries(data_json)
    Session.add_all(campus_eateries)
    Session.commit()

    yelp_query = collegetown_search()
    collegetown_eateries = parse_collegetown_eateries(yelp_query)
    Session.add_all(collegetown_eateries)
    Session.commit()


# except Exception as e:
# print("Data update failed:", e)


start_update()
