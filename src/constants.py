from datetime import datetime
import pytz

ACCOUNT_NAMES = {
    "brbs": "BRB Big Red Bucks",
    "citybucks": "CB1 City Bucks",
    "cornell_card": "CC1 Cornell Card",
    "laundry": "LAU Sem Laundry",
}
BRB_ONLY = "brb_only"
CORNELL_DINING_URL = "https://now.dining.cornell.edu/api/1.0/dining/eateries.json"
CORNELL_INSTITUTION_ID = "73116ae4-22ad-4c71-8ffd-11ba015407b1"
DINING_HALL = "dining_hall"
EATERY_DATA_PATH = "./eatery-data/"
GET_LOCATIONS = {
    "Attrium Cafe": "Atrium Café",
    "Bear Necessities Grill & C-Store": "Bear Necessities",
    "Goldies Cafe": "Goldie's Café",
    "Jansens Market": "Jansen's Market",
    "Olin Libe Cafe": "Libe Café",
    "Physical Science 1stFlr": "PSB Snack",
    "Straight From The": "Straight from the Market",
}
GET_URL = "https://services.get.cbord.com/GETServices/services/json"
GIT_CONTENT_URL = "https://raw.githubusercontent.com/cuappdev"
IGNORE_LOCATIONS = ["BS-No Bill Workstation", "Admin Workstation (B)", "GET Location"]
IMAGES_URL = GIT_CONTENT_URL + "/assets/master/eatery/eatery-images/"
TRILLIUM = "trillium"
TRILLIUM_ID = 23
TRILLIUM_SLUG = "Trillium"
LOCATION_NAMES = {
    "Alice Cook House": {"name": "Cook House Dining Room", "type": DINING_HALL},
    "Bear Necessities": {"name": "Bear Necessities Grill & C-Store", "type": BRB_ONLY},
    "Big Red Barn": {"name": "Big Red Barn", "type": BRB_ONLY},
    "Bus Stop Bagels": {"name": "Bus Stop Bagels", "type": BRB_ONLY},
    "Cafe Jennie": {"name": "Café Jennie", "type": BRB_ONLY},
    "Carl Becker House": {"name": "Becker House Dining Room", "type": DINING_HALL},
    "Carols Cafe": {"name": "Carol's Café", "type": BRB_ONLY},
    "Duffield": {"name": "Mattin's Café", "type": BRB_ONLY},
    "Franny's FT": {"name": "Franny's", "type": BRB_ONLY},
    "Goldie's Cafe": {"name": "Goldie's Café", "type": BRB_ONLY},
    "Green Dragon": {"name": "Green Dragon", "type": BRB_ONLY},
    "Ivy Room": {"name": "Ivy Room", "type": BRB_ONLY},
    "Jansens at Bethe House": {"name": "Jansen's Dining Room at Bethe House", "type": DINING_HALL},
    "Jansen's Market": {"name": "Jansen's Market", "type": BRB_ONLY},
    "Keeton House": {"name": "Keeton House Dining Room", "type": DINING_HALL},
    "Kosher": {"name": "104West!", "type": DINING_HALL},
    "Marthas": {"name": "Martha's Express", "type": BRB_ONLY},
    "McCormick's": {"name": "McCormick's at Moakley House", "type": BRB_ONLY},
    "North Star Marketplace": {"name": "North Star Dining Room", "type": DINING_HALL},
    "Okenshields": {"name": "Okenshields", "type": DINING_HALL},
    "Olin Libe Cafe": {"name": "Amit Bhatia Libe Café", "type": BRB_ONLY},
    "RPME": {"name": "Robert Purcell Marketplace Eatery", "type": DINING_HALL},
    "Risley": {"name": "Risley Dining Room", "type": DINING_HALL},
    "Rose House": {"name": "Rose House Dining Room", "type": DINING_HALL},
    "Rustys": {"name": "Rusty's", "type": BRB_ONLY},
    "Sage": {"name": "Atrium Café", "type": BRB_ONLY},
    "Statler Macs": {"name": "Mac's Café", "type": BRB_ONLY},
    "Statler Terrace": {"name": "The Terrace", "type": BRB_ONLY},
    "Straight Market": {"name": "Straight from the Market", "type": BRB_ONLY},
    "Trillium": {"name": "Trillium", "type": TRILLIUM},
}
NUM_DAYS_STORED_IN_DB = 8
PAY_METHODS = {
    "brbs": "Meal Plan - Debit",
    "c-card": "Cornell Card",
    "credit": "Major Credit Cards",
    "mobile": "Mobile Payments",
    "swipes": "Meal Plan - Swipe",
}
POSITIVE_TRANSACTION_TYPE = 3
SCHOOL_BREAKS = {
    "fall": "10/12/19-10/15/19",
    "thanksgiving": "11/27/19-12/01/19",
    "finals_winter": "12/11/19-12/21/19",
    "winter": "12/22/19-1/20/20",
    "february": "2/22/20-2/25/20",
    "spring": "3/28/20-4/5/20",
    "finals_spring": "5/6/20-5/16/20",
    "summer": "5/17/20-8/27/20",
}
SQLITE_MAX_VARIABLE_NUMBER = 999
STATIC_SOURCES_URL = GIT_CONTENT_URL + "/eatery-backend/master/static_sources/"
STATIC_CTOWN_HOURS_URL = STATIC_SOURCES_URL + "externalHours.json"
STATIC_EATERIES_URL = STATIC_SOURCES_URL + "externalEateries.json"
STATIC_EATERY_SLUGS = [
    "Anabels-Grocery",
    "Fork-and-Gavel",
    "Gimme-Coffee",
    "Louies-Lunch",
    "Macs",
    "Manndible",
    "Terrace",
    "Zeus",
]
STATIC_EXPANDED_ITEMS_URL = STATIC_SOURCES_URL + "expandedItems.json"
STATIC_MENUS_URL = STATIC_SOURCES_URL + "hardcodedMenus.json"
SWIPE_DENSITY_ROUND = 3
SWIPE_PLANS = ["Bear Basic", "Bear Choice", "Bear Traditional", "Flex 10/500", "Off", "Unlimited"]
TABLE_COLUMNS = ["date", "session_type", "weekday", "location", "start_time", "end_time", "swipes", "multiplier"]
UPDATE_DELAY = 86400  # 24 hours in seconds
UPDATE_DELAY_TESTING = 60  # 1 minute in seconds
# default multiplier for converting average swipes/count to wait time
WAIT_TIME_CONVERSION = {BRB_ONLY: 0.06, DINING_HALL: 0.05, TRILLIUM: 0.03}
WEEKDAYS = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
YELP_LATITUDE = 42.440680
YELP_LONGITUDE = -76.486043
YELP_RADIUS = 200  # meters
YELP_RESTAURANT_LIMIT = 50  # maximum restaurants returned per query (as allowed by yelp)
YELP_QUERY_DELAY = 0.8  # seconds


def get_today():
    return datetime.now(pytz.timezone("US/Eastern")).date()
