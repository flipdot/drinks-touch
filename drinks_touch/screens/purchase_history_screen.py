from screens.screen import Screen


class PurchaseHistoryScreen(Screen):

    def __init__(self):
        super().__init__()

    def on_start(self, *args, **kwargs):
        from time import sleep

        sleep(3)
