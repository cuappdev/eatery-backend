from graphene import Boolean, Enum, ObjectType

class PaymentMethodsEnum(Enum):
  BRB = 0
  CASH = 1
  CORNELL_CARD = 2
  CREDIT = 3
  MOBILE = 4
  SWIPES = 5

class PaymentMethodsType(ObjectType):
  brbs = Boolean(required=True)
  cash = Boolean(required=True)
  cornell_card = Boolean(required=True)
  credit = Boolean(required=True)
  mobile = Boolean(required=True)
  swipes = Boolean(required=True)
