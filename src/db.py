from datetime import datetime
import requests

from collegetown import collegetown_search
from constants import CORNELL_DINING_URL, STATIC_EATERIES_URL, STATIC_EATERY_SLUGS
from database import CampusEatery, CollegetownEatery, CollegetownEateryHour, Base, Engine, Session, SwipeData
from eatery_db import (
    export_data,
    parse_campus_eateries,
    parse_campus_hours,
    parse_collegetown_eateries,
    parse_collegetown_hours,
    parse_menu_categories,
    parse_menu_items,
    parse_static_eateries,
    parse_static_op_hours,
    parse_to_csv,
)


def get_campus_eateries(data_json, refresh=False):
    campus_eateries = CampusEatery.query.all()

    if refresh:
        Base.metadata.drop_all(bind=Engine)
        Base.metadata.create_all(bind=Engine)
        print("[{}] Updating campus eateries".format(datetime.now()))
        campus_eateries = parse_campus_eateries(data_json)
        Session.add_all(campus_eateries)
        Session.commit()

    return campus_eateries


def start_update(refresh_campus=False, recalculate_swipe=False):
    try:
        print("[{}] Fetching campus eateries".format(datetime.now()))
        campus_json = requests.get(CORNELL_DINING_URL).json()
        campus_eateries = get_campus_eateries(campus_json, refresh=refresh_campus)

        if recalculate_swipe:
            print("[{}] Updating swipe data".format(datetime.now()))
            data_path = parse_to_csv(file_name="data.csv")
            Base.metadata.drop_all(bind=Engine, tables=[SwipeData.__table__])
            Base.metadata.create_all(bind=Engine, tables=[SwipeData.__table__])
            all_swipe_data = export_data(data_path, campus_eateries)
            Session.add_all(all_swipe_data)
            Session.commit()

        print("[{}] Updating campus eatery hours and menus".format(datetime.now()))
        for eatery in campus_eateries:
            # if this is not a refresh, then static eateries are part of campus_eateries
            if eatery.slug not in STATIC_EATERY_SLUGS:
                hours_and_menus = parse_campus_hours(campus_json, eatery)
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

                campus_eateries.remove(eatery)

        print("[{}] Fetching static campus eateries".format(datetime.now()))
        static_json = requests.get(STATIC_EATERIES_URL).json()
        static_eateries = campus_eateries

        if refresh_campus:
            print("[{}] Updating static campus eateries".format(datetime.now()))
            static_eateries = parse_static_eateries(static_json)
            Session.add_all(static_eateries)
            Session.commit()

        print("[{}] Updating static eatery hours and menus".format(datetime.now()))
        for eatery in static_eateries:
            hours_and_menus = parse_static_op_hours(static_json, eatery)
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

        Base.metadata.drop_all(bind=Engine, tables=[CollegetownEatery.__table__, CollegetownEateryHour.__table__])
        Base.metadata.create_all(bind=Engine, tables=[CollegetownEatery.__table__, CollegetownEateryHour.__table__])
        print("[{}] Fetching Collegetown eateries".format(datetime.now()))
        yelp_query = collegetown_search()
        collegetown_eateries = parse_collegetown_eateries(yelp_query)
        Session.add_all(collegetown_eateries)
        Session.commit()

        print("[{}] Updating Collegetown eateries and hours".format(datetime.now()))
        for eatery in collegetown_eateries:
            hours = parse_collegetown_hours(yelp_query, eatery)
            Session.add_all(hours)
            Session.commit()

    except Exception as e:
        print("Data update failed:", e)


start_update(True, True)
