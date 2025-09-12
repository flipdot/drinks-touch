from database.models import Drink


class DrinksManager:
    instance = None

    def __init__(self):
        assert DrinksManager.instance is None, "DrinksManager is a singleton"
        self.selected_drink: Drink | None = None
        DrinksManager.instance = self

    def set_selected_drink(self, drink: Drink | None):
        self.selected_drink = drink

    def get_selected_drink(self) -> Drink | None:
        return self.selected_drink
