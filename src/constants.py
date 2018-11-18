ACCOUNT_NAMES = {
    'brbs': 'BRB Big Red Bucks',
    'citybucks': 'CB1 City Bucks',
    'cornell_card': 'CC1 Cornell Card',
    'laundry': 'LAU Sem Laundry'
    # 'swipes': TBD
}
CORNELL_DINING_URL = 'https://now.dining.cornell.edu/api/1.0/dining/eateries.json'
CORNELL_INSTITUTION_ID = '73116ae4-22ad-4c71-8ffd-11ba015407b1'
GET_URL = 'https://services.get.cbord.com/GETServices/services/json'
GIT_CONTENT_URL = 'https://raw.githubusercontent.com/cuappdev'
IMAGES_URL = GIT_CONTENT_URL + '/assets/master/eatery/eatery-images/'
NUM_DAYS_STORED_IN_DB = 8
PAY_METHODS = {
    'brbs': 'Meal Plan - Debit',
    'c-card': 'Cornell Card',
    'credit': 'Major Credit Cards',
    'mobile': 'Mobile Payments',
    'swipes': 'Meal Plan - Swipe'
}
STATIC_EATERIES_URL = GIT_CONTENT_URL + '/DiningStack/master/DiningStack/externalEateries.json'
STATIC_MENUS_URL = GIT_CONTENT_URL + '/DiningStack/master/DiningStack/hardcodedMenus.json'
TRILLIUM_ID = 23
UPDATE_DELAY = 86400  # 24 hours in seconds
UPDATE_DELAY_TESTING = 60  # 1 minute in seconds
# [M, T, W, Th, F, St, S]
# [0, 1, 2, 3, 4, 5, 6]
WEEKDAYS = {
    'monday-wednesday': [0, 1, 2],
    'monday-thursday': [0, 1, 2, 3],
    'monday-friday': [0, 1, 2, 3, 4],
    'thursday': [3],
    'friday': [4],
    'saturday': [5],
    'sunday': [6]
}
YELP_LATITUDE = 42.440680
YELP_LONGITUDE = -76.486043
YELP_NUMBER_LIMIT = 50
YELP_RADIUS = 200  # units meters
YELP_QUERY_DELAY = .1  # units seconds
