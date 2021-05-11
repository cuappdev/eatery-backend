from graphene import Boolean, List, ObjectType, String


class TransactionType(ObjectType):
    amount = String(required=True)
    name = String(required=True)
    positive = Boolean(required=True)
    timestamp = String(required=True)


class AccountInfoType(ObjectType):
    brbs = String(required=True)
    city_bucks = String(required=True)
    history = List(TransactionType, required=True)
    laundry = String(required=True)
    swipes = String(required=True)
    favorites = List(String, required=True)
