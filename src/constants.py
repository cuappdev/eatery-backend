ACCOUNT_NAMES = {
    'brbs': 'BRB Big Red Bucks',
    'citybucks': 'CB1 City Bucks',
    'cornell_card': 'CC1 Cornell Card',
    'laundry': 'LAU Sem Laundry'
}
CORNELL_DINING_URL = 'https://now.dining.cornell.edu/api/1.0/dining/eateries.json'
CORNELL_INSTITUTION_ID = '73116ae4-22ad-4c71-8ffd-11ba015407b1'
GET_URL = 'https://services.get.cbord.com/GETServices/services/json'
GIT_CONTENT_URL = 'https://raw.githubusercontent.com/cuappdev'
IGNORE_LOCATIONS = ['BS-No Bill Workstation', 'Admin Workstation (B)']
IMAGES_URL = GIT_CONTENT_URL + '/assets/master/eatery/eatery-images/'
LOCATION_NAMES = {
  'Alice Cook House': 'Cook House Dining Room',
  'Attrium Cafe': 'Atrium Café',
  'Bear Necessities': 'Bear Necessities Grill & C-Store',
  'Big Red Barn': 'Big Red Barn',
  'Bus Stop Bagels': 'Bus Stop Bagels',
  'Cafe Jennie': 'Café Jennie',
  'Carl Becker House': 'Becker House Dining Room',
  'Carols Cafe': "Carol's Café",
  'Duffield': "Mattin's Café",
  "Franny's FT": "Franny's",
  "Goldies Cafe": "Goldie's Café",
  "Goldie's Cafe": "Goldie's Café",
  'Green Dragon': 'Green Dragon',
  'Ivy Room': 'Ivy Room',
  'Jansens at Bethe House': "Jansen's Dining Room at Bethe House",
  'Jansens Market': "Jansen's Market",
  "Jansen's Market": "Jansen's Market",
  'Keeton House': 'Keeton House Dining Room',
  'Kosher': '104West!',
  'Marthas': "Martha's Express",
  "McCormick's": "McCormick's at Moakley House",
  'North Star Marketplace': 'North Star Dining Room',
  'Okenshields': 'Okenshields',
  'Olin Libe Cafe': 'Amit Bhatia Libe Café',
  'Olin Libe Cafe2': 'Libe Café',
  'RPME': 'Robert Purcell Marketplace Eatery',
  'Risley': 'Risley Dining Room',
  'Rose House': 'Rose House Dining Room',
  'Rustys': "Rusty's",
  'Sage': 'Atrium Café',
  'Statler Macs': "Mac's Café",
  'Statler Terrace': 'The Terrace',
  'Straight Market': 'Straight from the Market',
  'Trillium': 'Trillium'
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
