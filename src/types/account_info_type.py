from graphene import Boolean, List, ObjectType, String


class TransactionType(ObjectType):
    """ TransactionType

    amount (String) --
    name (String) --
    positive (Boolean) --
    timestamp (String) --
    """

    amount = String(required=True)
    name = String(required=True)
    positive = Boolean(required=True)
    timestamp = String(required=True)


class AccountInfoType(ObjectType):
    """ AccountInfoType

    brbs (String) --
    city_bucks (String) --
    history (List[TransactionType]) --
    laundry (String) --
    swipes (String) --
    """

    brbs = String(required=True)
    city_bucks = String(required=True)
    history = List(TransactionType, required=True)
    laundry = String(required=True)
    swipes = String(required=True)
