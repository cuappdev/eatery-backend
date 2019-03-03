from graphene import Float, Int, ObjectType, String

class SwipeDataType(ObjectType):
  session_type = String(required=True)
  end_time = String(required=True)
  start_time = String(required=True)
  swipe_density = Float(required=True)
  wait_time_high = Int(required=True)
  wait_time_low = Int(required=True)
