from graphene import Float, Int, ObjectType, String


class SwipeDataType(ObjectType):
    end_time = String(required=True)
    session_type = String(required=True)
    start_time = String(required=True)
    swipe_density = Float(required=True)
    wait_time_high = Int(required=True)
    wait_time_low = Int(required=True)
