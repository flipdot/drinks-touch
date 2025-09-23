import config
from config import Color
from elements import Label, Image
from elements.hbox import HBox
from elements.spacer import Spacer
from elements.vbox import VBox
from screens import screen
from users.qr import make_qr_code


class AddNewDrinkScreen(screen.Screen):

    def __init__(self, ean: str):
        super().__init__()
        self.ean = ean

    def on_start(self, *args, **kwargs):
        url = f"{config.BASE_URL}/drinks/new/{self.ean}"
        self.objects = [
            Label(
                text="Neues Getränk",
                size=40,
                pos=(5, 5),
            ),
            VBox(
                [
                    Label(text="Preis und Name festlegen unter:", size=28),
                    Spacer(height=100),
                    HBox(
                        [
                            Spacer(width=config.SCREEN_WIDTH / 5),
                            Image(
                                src=make_qr_code(
                                    url,
                                    pixel_width=7,
                                    border=4,
                                    color="black",
                                    bg=Color.PRIMARY.value,
                                )
                            ),
                        ]
                    ),
                    Label(text=url, size=16),
                ],
                pos=(5, 200),
            ),
        ]

    def on_barcode(self, barcode):
        from screens.drink_scanned import DrinkScannedScreen

        self.goto(DrinkScannedScreen(barcode), replace=True)
