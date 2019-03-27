<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from graphene import Float, Int, ObjectType, String
=======
from graphene import Boolean, Float, ObjectType, String
>>>>>>> Transfer swipe data into CampusEateryType
=======
from graphene import Float, ObjectType, String
>>>>>>> Replace in_session with session_type
=======
from graphene import Float, Int, ObjectType, String
>>>>>>> Differentiate wait time conversion multipliers by eatery type

class SwipeDataType(ObjectType):
<<<<<<< HEAD
  session_type = String(required=True)
  end_time = String(required=True)
  start_time = String(required=True)
  swipe_density = Float(required=True)
  wait_time_high = Int(required=True)
  wait_time_low = Int(required=True)
=======
  average_swipes = Float(required=True)
  session_type = String(required=True)
  end_time = String(required=True)
  start_time = String(required=True)
<<<<<<< HEAD
>>>>>>> Add documentation
=======
  wait_time_high = Int(required=True)
  wait_time_low = Int(required=True)
>>>>>>> Differentiate wait time conversion multipliers by eatery type
