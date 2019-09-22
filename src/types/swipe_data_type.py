from graphene import Float, Int, ObjectType, String


class SwipeDataType(ObjectType):
    """ SwipeDataType

    end_time (String) --
    session_type (String) --
    start_time (String) --
    swipe_density (Float) --
    wait_time_high (Int) --
    wait_time_low (Int) --
    """

    end_time = String(required=True)
    session_type = String(required=True)
    start_time = String(required=True)
    swipe_density = Float(required=True)
    wait_time_high = Int(required=True)
    wait_time_low = Int(required=True)
