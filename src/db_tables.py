from src.db_models.CampusEatery import CampusEatery
from src.db_models.CampusEateryHour import CampusEateryHour
from src.db_models.CollegetownEatery import CollegetownEatery
from src.db_models.CollegetownEateryHour import CollegetownEateryHour
from src.db_models.ExpandedMenu import ExpandedMenu
from src.db_models.Menu import Menu
from src.db_models.SwipeData import SwipeData
from src.db_setup import engine, Base

campusEateries = type("CampusEatery", (CampusEatery, Base), {})
campusEateryHours = type("CampusEateryHour", (CampusEateryHour, Base), {})
collegetownEateries = type("CollegetownEatery", (CollegetownEatery, Base), {})
collegetownEateryHours = type("CollegetownEateryHour", (CollegetownEateryHour, Base), {})
expandedMenus = type("ExpandedMenu", (ExpandedMenu, Base), {})
menus = type("Menu", (Menu, Base), {})
swipeDatas = type("SwipeData", (SwipeData, Base), {})

Base.metadata.create_all(bind=engine)
