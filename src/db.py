from datetime import datetime
import requests

# from collegetown import collegetown_search
from constants import CORNELL_DINING_URL
from database import Base, Engine, Session
from eatery_db import parse_campus_eateries, parse_campus_hours, parse_menu_categories, parse_menu_items


def start_update():
    # try:
    Base.metadata.drop_all(bind=Engine)
    Base.metadata.create_all(bind=Engine)

    print("[{}] Updating campus eateries".format(datetime.now()))
    dining_query = requests.get(CORNELL_DINING_URL)
    data_json = dining_query.json()
    campus_eateries = parse_campus_eateries(data_json)
    Session.add_all(campus_eateries)
    Session.commit()

    print("[{}] Updating campus eatery hours and menus".format(datetime.now()))
    for eatery in campus_eateries:
        hours_and_menus = parse_campus_hours(data_json, eatery)
        eatery_hours = (x[0] for x in hours_and_menus)
        Session.add_all(eatery_hours)
        Session.commit()

        for eatery_hour, menu_json in hours_and_menus:
            categories_and_items = parse_menu_categories(menu_json, eatery_hour)
            eatery_categories = (x[0] for x in categories_and_items)
            Session.add_all(eatery_categories)
            Session.commit()

            for menu_category, items_json in categories_and_items:
                menu_items = parse_menu_items(items_json, menu_category)
                Session.add_all(menu_items)
                Session.commit()

    """
        Let's not do this right now, Collegetown updates take a long time

        print("[{}] Updating collegetown".format(datetime.now()))
        yelp_query = collegetown_search()
        collegetown_eateries = parse_collegetown_eateries(yelp_query)
        Session.add_all(collegetown_eateries)
        Session.commit()
        """


# except Exception as e:
#    print("Data update failed:", e)


start_update()
