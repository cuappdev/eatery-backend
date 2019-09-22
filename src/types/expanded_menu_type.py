from graphene import List, ObjectType, String

from src.types.food_station_type import FoodItemType, FoodStationType


class DescriptiveFoodItemOptionType(ObjectType):
    """ DescriptiveFoodItemOptionType

    label (String) -- Name of choice category (e.g. Bread)
    options (List[String]) -- All options offered for the category (e.g. "Multigrain", "Ciabatta", "Kaiser roll",
                              "Plain wrap")
    """

    label = String(required=True)
    options = List(String, required=True)


class DescriptiveFoodItemType(FoodItemType):
    """ DescriptiveFoodItemType

    choices (List[DescriptiveFoodItemOptionType]) -- Customization choices available
    price (String) -- Price of item
    """

    choices = List(DescriptiveFoodItemOptionType, required=False)
    price = String(required=True)

    def equals(self, food_item):
        if len(self.options) != len(food_item.options):
            return False
        # Check equals using the FoodItemType and with new fields
        return (
            super(FoodItemType, self).equals(self, food_item)
            and self.price == food_item.price
            and all([self.options[i].equals(food_item.options[i]) for i in range(self.options)])
        )


class DescriptiveFoodStationType(FoodStationType):
    """ DescriptiveFoodStationType

    items (List[DescriptiveFoodItemType]) -- Details of menu items
    """

    items = List(DescriptiveFoodItemType, required=True)


class FoodCategoryType(ObjectType):
    """ FoodCategoryType

    category (String) -- Category of menu items (e.g. Main)
    stations (List[DescriptiveFoodStationType]) -- Menu items separated by categories
    """

    category = String(required=True)
    stations = List(DescriptiveFoodStationType, required=True)
