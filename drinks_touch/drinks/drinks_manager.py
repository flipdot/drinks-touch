class DrinksManager:
    instance = None

    def __init__(self):
        assert DrinksManager.instance is None, "DrinksManager is a singleton"
        self.selected_barcode: str | None = None
        DrinksManager.instance = self
