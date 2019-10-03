from datetime import datetime, timedelta
from dateutil import parser
from graphene import Field, Int, List, ObjectType, String
import pytz
import requests

from src.constants import (
    ACCOUNT_NAMES,
    CORNELL_INSTITUTION_ID,
    GET_LOCATIONS,
    GET_URL,
    IGNORE_LOCATIONS,
    LOCATION_NAMES,
    POSITIVE_TRANSACTION_TYPE,
    SWIPE_PLANS,
)
from src.types import AccountInfoType, CampusEateryType, CollegetownEateryType, TransactionType


class Data(object):
    campus_eateries = {}
    collegetown_eateries = {}

    @staticmethod
    def update_data(campus_eateries):
        Data.campus_eateries = campus_eateries

    @staticmethod
    def update_collegetown_data(collegetown_eateries):
        Data.collegetown_eateries = collegetown_eateries


class Query(ObjectType):
    account_info = Field(AccountInfoType, session_id=String(name="id"))
    campus_eateries = List(CampusEateryType, eatery_id=Int(name="id"))
    collegetown_eateries = List(CollegetownEateryType, eatery_id=Int(name="id"))
    eateries = List(CampusEateryType, eatery_id=Int(name="id"))

    def get_eateries(eateries, eatery_id):
        if eatery_id is None:
            return list(eateries.values())
        eatery = eateries.get(eatery_id)
        return [eatery] if eatery is not None else []

    def resolve_campus_eateries(self, info, eatery_id=None):
        return Query.get_eateries(Data.campus_eateries, eatery_id)

    def resolve_collegetown_eateries(self, info, eatery_id=None):
        return Query.get_eateries(Data.collegetown_eateries, eatery_id)

    def resolve_eateries(self, info, eatery_id=None):
        return Query.get_eateries(Data.campus_eateries, eatery_id)

    def resolve_account_info(self, info, session_id=None):
        if session_id is None:
            return "Provide a valid session ID!"

        account_info = {}

        # Query 1: Get user id
        try:
            user_id = requests.post(
                GET_URL + "/user", json={"version": "1", "method": "retrieve", "params": {"sessionId": session_id}}
            ).json()["response"]["id"]
        except:
            user_id = {}

        # Query 2: Get finance info
        try:
            accounts = requests.post(
                GET_URL + "/commerce",
                json={
                    "version": "1",
                    "method": "retrieveAccountsByUser",
                    "params": {"sessionId": session_id, "userId": user_id},
                },
            ).json()["response"]["accounts"]
        except:
            accounts = {}

        # intialize default values
        account_info["brbs"] = "0.00"
        account_info["city_bucks"] = "0.00"
        account_info["laundry"] = "0.00"
        account_info["swipes"] = "0"
        for acct in accounts:
            if acct["accountDisplayName"] == ACCOUNT_NAMES["citybucks"]:
                account_info["city_bucks"] = str("{0:.2f}".format(round(acct["balance"], 2)))
            elif acct["accountDisplayName"] == ACCOUNT_NAMES["laundry"]:
                account_info["laundry"] = str("{0:.2f}".format(round(acct["balance"], 2)))
            elif ACCOUNT_NAMES["brbs"] in acct["accountDisplayName"]:
                account_info["brbs"] = str("{0:.2f}".format(round(acct["balance"], 2)))
            elif any(meal_swipe_name in acct["accountDisplayName"] for meal_swipe_name in SWIPE_PLANS):
                account_info["swipes"] = str(acct["balance"])

        # Check if the balance provided by Cornell Dining is a regular digit
        if account_info["swipes"].isdigit():
            # Check if the meal plan has more than 50 swipes, this is larger than the largest plan.
            if int(account_info["swipes"]) > 50:
                account_info["swipes"] = "Unlimited"

        # Query 3: Get list of transactions
        try:
            transactions = requests.post(
                GET_URL + "/commerce",
                json={
                    "method": "retrieveTransactionHistory",
                    "params": {
                        "paymentSystemType": 0,
                        "queryCriteria": {
                            "accountId": None,
                            "endDate": str(datetime.now().date()),
                            "institutionId": CORNELL_INSTITUTION_ID,
                            "maxReturn": 100,
                            "startDate": str((datetime.now() - timedelta(weeks=32)).date()),
                            "startingReturnRow": None,
                            "userId": user_id,
                        },
                        "sessionId": session_id,
                    },
                    "version": "1",
                },
            ).json()["response"]["transactions"]
        except:
            transactions = {}

        account_info["history"] = []

        for txn in transactions:
            if ACCOUNT_NAMES["brbs"] not in txn["accountName"] or txn["locationName"] in IGNORE_LOCATIONS:
                continue
            txn_timestamp = parser.parse(txn["actualDate"]).astimezone(pytz.timezone("US/Eastern"))
            location = txn["locationName"].rsplit(" ", 1)[0]
            # removes the register numbers at the end of the string by taking the substring up until
            # the last space (right before the number)

            if location in GET_LOCATIONS:
                name = GET_LOCATIONS[location]
            elif location in LOCATION_NAMES:
                name = LOCATION_NAMES[location]["name"]
            elif "Vending" in location:
                name = "Vending Machine"
            else:
                name = location

            positive = txn["transactionType"] == POSITIVE_TRANSACTION_TYPE

            new_transaction = {
                "amount": "{:.2f}".format(float(txn["amount"])),
                "name": name,
                "positive": positive,
                "timestamp": txn_timestamp.strftime("%A, %b %d at %I:%M %p"),
            }
            account_info["history"].append(TransactionType(**new_transaction))

        return AccountInfoType(**account_info)
