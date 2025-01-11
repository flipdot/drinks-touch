class DrinksManager:
    instance = None

    def __init__(self):
        assert DrinksManager.instance is None, "DrinksManager is a singleton"
        self.selected_drink = None
        DrinksManager.instance = self

    def set_selected_drink(self, drink):
        self.selected_drink = drink

    def get_selected_drink(self):
        return self.selected_drink
