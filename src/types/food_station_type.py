from graphene import Boolean, Int, List, ObjectType, String

class FoodItemType(ObjectType):
  item = String(required=True)
  healthy = Boolean(required=True)

  def equals(self, food_item):
    return self.item == food_item.item and self.healthy == food_item.healthy

class FoodStationType(ObjectType):
  category = String(required=True)
  items = List(FoodItemType, required=True)

  def equals(self, food_station):
    num_items = len(self.items)
    if num_items != len(food_station.items):
      return False
    # check if each item in menu equals the item in other menu
    return all([self.items[i].equals(food_station.items[i]) for i in range(num_items)])
