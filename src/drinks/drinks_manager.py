class DrinksManager:
    instance = None

    def __init__(self):
        self.selected_drink = None

    @staticmethod
    def get_instance():
        return DrinksManager.instance

    @staticmethod
    def set_instance(instance):
        DrinksManager.instance = instance

    def set_selected_drink(self, drink):
        self.selected_drink = drink

    def get_selected_drink(self):
        return self.selected_drink        