ACCOUNT_NAMES = {
    'brbs': 'BRB Big Red Bucks',
    'citybucks': 'CB1 City Bucks',
    'cornell_card': 'CC1 Cornell Card',
    'laundry': 'LAU Sem Laundry'
}
BRB_ONLY = 'brb_only'
CORNELL_DINING_URL = 'https://now.dining.cornell.edu/api/1.0/dining/eateries.json'
CORNELL_INSTITUTION_ID = '73116ae4-22ad-4c71-8ffd-11ba015407b1'
DINING_HALL = 'dining_hall'
EATERY_DATA_PATH = './eatery-data/'
GET_URL = 'https://services.get.cbord.com/GETServices/services/json'
GIT_CONTENT_URL = 'https://raw.githubusercontent.com/cuappdev'
IGNORE_LOCATIONS = ['BS-No Bill Workstation', 'Admin Workstation (B)']
IMAGES_URL = GIT_CONTENT_URL + '/assets/master/eatery/eatery-images/'
ISOLATE_SWIPES = ['date', 'session_type', 'weekday', 'location', 'start_time', 'end_time', 'dining_hall', 'brb_only']
ISOLATE_DATE = ['session_type', 'weekday', 'location', 'start_time', 'end_time', 'swipes', 'dining_hall', 'brb_only']
ISOLATE_COUNTER_SWIPES = ['session_type', 'weekday', 'location', 'start_time', 'end_time', 'dining_hall', 'brb_only']
LOCATION_NAMES = {
  'Alice Cook House': {'name': 'Cook House Dining Room', 'type': DINING_HALL},
  'Attrium Cafe': {'name': 'Atrium Café'},  # for GET history
  'Bear Necessities': {'name': 'Bear Necessities Grill & C-Store', 'type': BRB_ONLY},
  'Big Red Barn': {'name': 'Big Red Barn', 'type': BRB_ONLY},
  'Bus Stop Bagels': {'name': 'Bus Stop Bagels', 'type': BRB_ONLY},
  'Cafe Jennie': {'name': 'Café Jennie', 'type': BRB_ONLY},
  'Carl Becker House': {'name': 'Becker House Dining Room', 'type': DINING_HALL},
  'Carols Cafe': {'name': "Carol's Café", 'type': BRB_ONLY},
  'Duffield': {'name': "Mattin's Café", 'type': BRB_ONLY},
  "Franny's FT": {'name': "Franny's", 'type': BRB_ONLY},
  "Goldies Cafe": {'name': "Goldie's Café"},  # for GET history
  "Goldie's Cafe": {'name': "Goldie's Café", 'type': BRB_ONLY},
  'Green Dragon': {'name': 'Green Dragon', 'type': BRB_ONLY},
  'Ivy Room': {'name': 'Ivy Room', 'type': BRB_ONLY},
  'Jansens at Bethe House': {'name': "Jansen's Dining Room at Bethe House", 'type': DINING_HALL},
  'Jansens Market': {'name': "Jansen's Market"},  # for GET history
  "Jansen's Market": {'name': "Jansen's Market", 'type': BRB_ONLY},
  'Keeton House': {'name': 'Keeton House Dining Room', 'type': DINING_HALL},
  'Kosher': {'name': '104West!', 'type': DINING_HALL},
  'Marthas': {'name': "Martha's Express", 'type': BRB_ONLY},
  "McCormick's": {'name': "McCormick's at Moakley House", 'type': BRB_ONLY},
  'North Star Marketplace': {'name': 'North Star Dining Room', 'type': DINING_HALL},
  'Okenshields': {'name': 'Okenshields', 'type': DINING_HALL},
  'Olin Libe Cafe': {'name': 'Amit Bhatia Libe Café', 'type': BRB_ONLY},
  'RPME': {'name': 'Robert Purcell Marketplace Eatery', 'type': DINING_HALL},
  'Risley': {'name': 'Risley Dining Room', 'type': DINING_HALL},
  'Rose House': {'name': 'Rose House Dining Room', 'type': DINING_HALL},
  'Rustys': {'name': "Rusty's", 'type': BRB_ONLY},
  'Sage': {'name': 'Atrium Café', 'type': BRB_ONLY},
  'Statler Macs': {'name': "Mac's Café", 'type': BRB_ONLY},
  'Statler Terrace': {'name': 'The Terrace', 'type': BRB_ONLY},
  'Straight Market': {'name': 'Straight from the Market', 'type': BRB_ONLY},
  'Trillium': {'name': 'Trillium', 'type': DINING_HALL},
}
NUM_DAYS_STORED_IN_DB = 8
PAY_METHODS = {
    'brbs': 'Meal Plan - Debit',
    'c-card': 'Cornell Card',
    'credit': 'Major Credit Cards',
    'mobile': 'Mobile Payments',
    'swipes': 'Meal Plan - Swipe'
}
SCHOOL_BREAKS = {
  'fall': '10/6/18-10/9/18',
  'thanksgiving': '11/21/18-11/25/18',
  'finals_winter': '12/5/18-12/15/18',
  'winter': '12/16/18-1/21/19',
  'february': '2/23/19-2/26/19',
  'spring': '3/30/19-4/7/19',
  'finals_spring': '5/8/19-5/18/19',
  'summer': '5/19/19-8/28/19'
}
STATIC_EATERIES_URL = GIT_CONTENT_URL + '/DiningStack/master/DiningStack/externalEateries.json'
STATIC_CTOWN_HOURS_URL = GIT_CONTENT_URL + '/DiningStack/master/DiningStack/externalHours.json'
STATIC_MENUS_URL = GIT_CONTENT_URL + '/DiningStack/master/DiningStack/hardcodedMenus.json'
SWIPE_PLANS = ['Bear Basic', 'Bear Choice', 'Bear Traditional']
TRILLIUM_ID = 23
UPDATE_DELAY = 86400  # 24 hours in seconds
UPDATE_DELAY_TESTING = 60  # 1 minute in seconds
# default multiplier for converting average swipes/count to wait time
WAIT_TIME_CONVERSION = { BRB_ONLY: .06, DINING_HALL: .05 }
WEEKDAYS = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}
YELP_LATITUDE = 42.440680
YELP_LONGITUDE = -76.486043
YELP_RADIUS = 200  # meters
YELP_RESTAURANT_LIMIT = 50  # maximum restaurants returned per query (as allowed by yelp)
YELP_QUERY_DELAY = 0.8  # seconds
