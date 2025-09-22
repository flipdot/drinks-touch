from database.models import Drink, Account


class GlobalState:
    selected_drink: Drink | None = None
    selected_account: Account | None = None

    @classmethod
    def reset(cls):
        cls.selected_drink = None
        cls.selected_account = None
