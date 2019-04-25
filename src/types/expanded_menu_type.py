from graphene import List, ObjectType, String

from src.types.food_station_type import FoodItemType, FoodStationType

class DescriptiveFoodItemOptionType(ObjectType):
  label = String(required=True)
  options = List(String, required=True)

class DescriptiveFoodItemType(FoodItemType):
  options = List(DescriptiveFoodItemOptionType, required=False)
  price = String(required=True)

  def equals(self, food_item):
    if len(self.options) == len(food_item.options):
      return False
    return (super(FoodItemType, self).equals(self, food_item) and self.price == food_item.price
            and all([self.options[i].equals(food_item.options[i]) for i in range(self.options)]))

class DescriptiveFoodStationType(FoodStationType):
  items = List(DescriptiveFoodItemType, required=True)

class FoodCategoryType(ObjectType):
  category = String(required=True)
  stations = List(DescriptiveFoodStationType, required=True)