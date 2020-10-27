from ..constants import SQLITE_MAX_VARIABLE_NUMBER
from ..db import conn
from ..database import (
    CampusEatery,
    CampusEateryHour,
    ExpandedMenuChoice,
    ExpandedMenuItem,
    ExpandedMenuStation,
    MenuCategory,
    MenuItem,
    SwipeData,
)
from ..gql_parser.common_eatery import parse_coordinates, parse_payment_methods, parse_payment_methods_enum
from ..gql_types import (
    CampusAreaType,
    CampusEateryType,
    EventType,
    FoodCategoryType,
    FoodItemType,
    FoodStationType,
    DescriptiveFoodItemOptionType,
    DescriptiveFoodItemType,
    DescriptiveFoodStationType,
    OperatingHoursType,
    SwipeDataType,
)


def get_campus_eateries(eatery_id):
    """Queries db to fetch information about a specific or all campus eateries.

    Returns a list of CampusEateryType objects.
    """
    if eatery_id is not None:
        query = CampusEatery.query.filter_by(id=eatery_id)
    else:
        query = CampusEatery.query

    result = conn.execute(query.statement).fetchall()
    columns = CampusEatery.__table__.columns.keys()

    populated_result = []
    for data in result:
        mapped_eatery = {}
        for i, column_name in enumerate(columns):
            mapped_eatery[column_name] = data[i]
        populated_eatery = parse_campus_eatery(mapped_eatery)
        populated_result.append(populated_eatery)

    merge_hours(populated_result)

    return populated_result


def parse_campus_eatery(eatery):
    """Parses eatery data from db and populates to an object.

    Returns a new CampusEateryType.
    """
    exceptions = eatery.get("exceptions")
    exceptions = [] if not exceptions else exceptions.split(";;")

    new_eatery = CampusEateryType(
        about=eatery.get("about", ""),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        eatery_type=eatery.get("eatery_type", ""),
        expanded_menu=parse_expanded_menu(eatery),
        id=eatery.get("id"),
        image_url=eatery.get("image_url"),
        location=eatery.get("location", ""),
        name=eatery.get("name", ""),
        name_short=eatery.get("name_short", ""),
        operating_hours=parse_operating_hours(eatery),
        payment_methods=parse_payment_methods(eatery),
        payment_methods_enums=parse_payment_methods_enum(eatery),
        phone=eatery.get("phone", "N/A"),
        slug=eatery.get("slug", ""),
        swipe_data=parse_swipe_data(eatery),
        exceptions=exceptions,
        reserve_link=eatery.get("reserve_link", ""),
        is_get=eatery.get("is_get", False),
    )
    return new_eatery


def parse_campus_area(eatery):
    """Parses the common name location of an eatery.

    Returns a new CampusAreaType that contains a description of an eatery.
    """
    campus_area = eatery.get("campus_area_desc", "")

    return CampusAreaType(description_short=campus_area)


def parse_expanded_menu(eatery):
    """Queries db for expanded menu stations, items, and chocies that are relevant to the specific eatery, then parses
    the information into appropriate data format.

    Returns a list FoodCategoryType objects.
    """
    # query for all menu STATIONs that will be needed to populate expanded menu
    query_stations = ExpandedMenuStation.query.filter_by(campus_eatery_id=eatery.get("id"))
    result_stations = conn.execute(query_stations.statement).fetchall()
    column_stations = ExpandedMenuStation.__table__.columns.keys()

    menu_to_station = {}
    station_ids = []
    for station in result_stations:
        mapped_station = {}
        for i, column_name in enumerate(column_stations):
            mapped_station[column_name] = station[i]

        menu_category = mapped_station["menu_category"]
        if menu_category in menu_to_station:
            menu_to_station[menu_category].append(mapped_station)
        else:
            menu_to_station[menu_category] = [mapped_station]
        station_ids.append(mapped_station["id"])

    # query for all menu ITEMs that will be needed to populate expanded menu
    result_items = []
    while station_ids:
        partial_query = ExpandedMenuItem.query.filter(
            ExpandedMenuItem.station_category_id.in_(station_ids[:SQLITE_MAX_VARIABLE_NUMBER])
        )
        partial_result = conn.execute(partial_query.statement).fetchall()
        result_items += partial_result
        station_ids = station_ids[SQLITE_MAX_VARIABLE_NUMBER:]
    column_items = ExpandedMenuItem.__table__.columns.keys()

    station_to_item = {}
    item_ids = []
    for item in result_items:
        mapped_item = {}
        for i, column_name in enumerate(column_items):
            mapped_item[column_name] = item[i]

        station_category = mapped_item["station_category_id"]
        if station_category in station_to_item:
            station_to_item[station_category].append(mapped_item)
        else:
            station_to_item[station_category] = [mapped_item]
        item_ids.append(mapped_item["id"])

    # query for all menu ITEMs that will be needed to populate expanded menu
    result_choices = []
    while item_ids:
        partial_query = ExpandedMenuChoice.query.filter(
            ExpandedMenuChoice.menu_item_id.in_(item_ids[:SQLITE_MAX_VARIABLE_NUMBER])
        )
        partial_result = conn.execute(partial_query.statement).fetchall()
        result_choices += partial_result
        item_ids = item_ids[SQLITE_MAX_VARIABLE_NUMBER:]
    column_choices = ExpandedMenuChoice.__table__.columns.keys()

    item_to_choice = {}
    for choice in result_choices:
        mapped_choice = {}
        for i, column_name in enumerate(column_choices):
            mapped_choice[column_name] = choice[i]

        menu_item = mapped_choice["menu_item_id"]
        if menu_item in item_to_choice:
            item_to_choice[menu_item].append(mapped_choice)
        else:
            item_to_choice[menu_item] = [mapped_choice]

    # Put together stations, items, and choices
    populated_result = []
    for menu_category in menu_to_station:
        stations_arr = menu_to_station[menu_category]
        station_objs_arr = []

        for station in stations_arr:
            items_arr = station_to_item.get(station["id"], [])
            item_objs_arr = []

            for item in items_arr:
                choices_arr = item_to_choice.get(item["id"], [])
                choice_objs_arr = []

                for choice in choices_arr:
                    options_arr = choice["options"].split(", ")
                    options = map(lambda x: x[1:-1], options_arr)
                    choice_obj = DescriptiveFoodItemOptionType(label=choice["label"], options=options)
                    choice_objs_arr.append(choice_obj)

                item_obj = DescriptiveFoodItemType(
                    item=item["item"], healthy=item["healthy"], price=item["price"], choices=choice_objs_arr
                )
                item_objs_arr.append(item_obj)

            station_obj = DescriptiveFoodStationType(category=station["station_category"], items=item_objs_arr)
            station_objs_arr.append(station_obj)

        result_obj = FoodCategoryType(category=menu_category, stations=station_objs_arr)
        populated_result.append(result_obj)

    return populated_result


def parse_operating_hours(eatery):
    """Queries db for operating hours, menu categories, and menu items that are relevant to the specific eatery,
    then parses the information into appropriate data format.

    Returns a list OperatingHoursType objects.
    """
    # query for all OPERATING_HOURs that will be needed to populate operating hours
    query_hours = CampusEateryHour.query.filter_by(eatery_id=eatery.get("id"))
    result_hours = conn.execute(query_hours.statement).fetchall()
    column_hours = CampusEateryHour.__table__.columns.keys()

    date_to_event = {}
    event_ids = []
    for hour in result_hours:
        mapped_hour = {}
        for i, column_name in enumerate(column_hours):
            mapped_hour[column_name] = hour[i]

        date = mapped_hour["date"]
        if not mapped_hour["start_time"]:
            date_to_event[date] = []
            continue

        if date in date_to_event:
            date_to_event[date].append(mapped_hour)
        else:
            date_to_event[date] = [mapped_hour]
        event_ids.append(mapped_hour["id"])

    # query for all MENU_CATEGORY that will be needed to populate operating hours
    result_categories = []
    while event_ids:
        partial_query = MenuCategory.query.filter(MenuCategory.event_id.in_(event_ids[:SQLITE_MAX_VARIABLE_NUMBER]))
        partial_result = conn.execute(partial_query.statement).fetchall()
        result_categories += partial_result
        event_ids = event_ids[SQLITE_MAX_VARIABLE_NUMBER:]
    column_categories = MenuCategory.__table__.columns.keys()

    event_to_category = {}
    category_ids = []
    for category in result_categories:
        mapped_category = {}
        for i, column_name in enumerate(column_categories):
            mapped_category[column_name] = category[i]

        event = category["event_id"]
        if event in event_to_category:
            event_to_category[event].append(mapped_category)
        else:
            event_to_category[event] = [mapped_category]
        category_ids.append(mapped_category["id"])

    # query for all MENU_ITEMs that will be needed to populate operating hours
    result_items = []
    while category_ids:
        partial_query = MenuItem.query.filter(MenuItem.category_id.in_(category_ids[:SQLITE_MAX_VARIABLE_NUMBER]))
        partial_result = conn.execute(partial_query.statement).fetchall()
        result_items += partial_result
        category_ids = category_ids[SQLITE_MAX_VARIABLE_NUMBER:]
    column_items = MenuItem.__table__.columns.keys()

    category_to_item = {}
    for item in result_items:
        mapped_item = {}
        for i, column_name in enumerate(column_items):
            mapped_item[column_name] = item[i]

        category = item["category_id"]
        if category in category_to_item:
            category_to_item[category].append(mapped_item)
        else:
            category_to_item[category] = [mapped_item]

    # query for all dining_items
    dining_item_category = {}
    dining_items_category_query = MenuCategory.query.filter_by(eatery_id=eatery.get("id"), event_id=None)
    dining_items_category_result = conn.execute(dining_items_category_query.statement).fetchall()
    for result in dining_items_category_result:
        for i, column_name in enumerate(column_categories):
            dining_item_category[column_name] = result[i]

    dining_items_arr = []
    dining_items_query = MenuItem.query.filter_by(category_id=dining_item_category.get("id"))
    dining_items_result = conn.execute(dining_items_query.statement).fetchall()
    for dining_item in dining_items_result:
        mapped_dining_item = {}
        for i, column_name in enumerate(column_items):
            mapped_dining_item[column_name] = dining_item[i]
        dining_items_arr.append(mapped_dining_item)

    # Put together hours, categories, and items
    populated_result = []
    for date in date_to_event:
        events_arr = date_to_event[date]
        events_objs_arr = []

        for event in events_arr:
            categories_arr = event_to_category.get(event["id"], [])
            if dining_item_category:
                categories_arr.append(dining_item_category)
                category_to_item[dining_item_category["id"]] = dining_items_arr
            categories_objs_arr = []

            for category in categories_arr:
                items_arr = category_to_item.get(category["id"], [])
                items_objs_arr = []

                for item in items_arr:
                    item_obj = FoodItemType(item=item["item"], healthy=item["healthy"])
                    items_objs_arr.append(item_obj)

                category_obj = FoodStationType(category=category["category"], items=items_objs_arr)
                categories_objs_arr.append(category_obj)

            events_obj = EventType(
                cal_summary=event["event_summary"],
                description=event["event_description"],
                end_time=event["end_time"],
                menu=categories_objs_arr,
                start_time=event["start_time"],
            )
            events_objs_arr.append(events_obj)

        result_obj = OperatingHoursType(date=date, events=events_objs_arr)
        populated_result.append(result_obj)

    return populated_result


def parse_swipe_data(eatery):
    """Queries db for an eatery's swipe data, then parses the information into appropriate data format.

    Returns a list SwipeDataType objects.
    """

    query = SwipeData.query.filter_by(eatery_id=eatery.get("id"))
    result = conn.execute(query.statement).fetchall()
    columns = SwipeData.__table__.columns.keys()

    populated_result = []
    for data in result:
        mapped_swipe_data = {}
        for i, column_name in enumerate(columns):
            mapped_swipe_data[column_name] = data[i]

        new_swipe_data = SwipeDataType(
            end_time=mapped_swipe_data["end_time"],
            session_type=mapped_swipe_data["session_type"],
            start_time=mapped_swipe_data["start_time"],
            swipe_density=mapped_swipe_data["swipe_density"],
            wait_time_high=mapped_swipe_data["wait_time_high"],
            wait_time_low=mapped_swipe_data["wait_time_low"],
        )
        populated_result.append(new_swipe_data)

    return populated_result


def merge_hours(eateries):
    """Merges invalid events with valid events

    Combines events with no menu and a start_time equal to the end_time of a previous event into
    one event. This removes the effectively removes the events with no menus and only preserves
    the end time of the invalid event.

    Args:
        eateries (list): A list filled with CampusEateryTypes
    """
    for eatery in eateries:
        for operating_hour in eatery.operating_hours:
            if len(operating_hour.events) <= 1:  # ignore hours that don't have multiple events
                continue
            base_event = operating_hour.events[0]
            for event in operating_hour.events[1:]:  # iterate over copy of list so we can safely remove
                if (
                    event.start_time == base_event.end_time
                    and base_event.menu
                    and (not event.menu or event.menu[0].equals(base_event.menu[0]))
                ):
                    base_event.end_time = event.end_time
                    operating_hour.events.remove(event)
                    print("merged events for {} on {}".format(eatery.name, operating_hour.date))
                else:
                    base_event = event
