from ..gql_types import CoordinatesType, PaymentMethodsEnum, PaymentMethodsType


def parse_coordinates(eatery):
    """Parses the coordinates of an eatery.

    Returns a new CoordinateType that holds the geographic coordinates of an eatery.
    """
    latitude = eatery.get("latitude", 0.0)
    longitude = eatery.get("longitude", 0.0)

    return CoordinatesType(latitude=latitude, longitude=longitude)


def parse_payment_methods(eatery):
    """Returns a PaymentMethodsType according to which payment methods are available at an eatery."""

    payment_method_brbs = eatery.get("payment_method_brbs")
    payment_method_cash = eatery.get("payment_method_cash")
    payment_method_cornell_card = eatery.get("payment_method_cornell_card")
    payment_method_credit = eatery.get("payment_method_credit")
    payment_method_mobile = eatery.get("payment_method_mobile")
    payment_method_swipes = eatery.get("payment_method_swipes")

    payment_methods = PaymentMethodsType(
        brbs=payment_method_brbs,
        cash=payment_method_cash,
        cornell_card=payment_method_cornell_card,
        credit=payment_method_credit,
        mobile=payment_method_mobile,
        swipes=payment_method_swipes,
    )
    return payment_methods


def parse_payment_methods_enum(eatery):
    """Returns a PaymentMethoddsEnumType according to which payment methods are available at an eatery."""

    payment_method_brbs = eatery.get("payment_method_brbs")
    payment_method_cash = eatery.get("payment_method_cash")
    payment_method_cornell_card = eatery.get("payment_method_cornell_card")
    payment_method_credit = eatery.get("payment_method_credit")
    payment_method_mobile = eatery.get("payment_method_mobile")
    payment_method_swipes = eatery.get("payment_method_swipes")
    payment_methods = []

    if payment_method_brbs:
        payment_methods.append(PaymentMethodsEnum.BRB)
    if payment_method_cash:
        payment_methods.append(PaymentMethodsEnum.CASH)
    if payment_method_cornell_card:
        payment_methods.append(PaymentMethodsEnum.CORNELL_CARD)
    if payment_method_credit:
        payment_methods.append(PaymentMethodsEnum.CREDIT)
    if payment_method_mobile:
        payment_methods.append(PaymentMethodsEnum.MOBILE)
    if payment_method_swipes:
        payment_methods.append(PaymentMethodsEnum.SWIPES)
    return payment_methods
