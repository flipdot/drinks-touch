from database.models import Drink


class GlobalState:
    selected_drink: Drink | None = None

    @classmethod
    def reset(cls):
        cls.selected_drink = None
