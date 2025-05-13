import config
from config import Font
from database.models import Account
from drinks.drinks import get_by_ean
from drinks.drinks_manager import DrinksManager
from elements.button import Button
from elements.label import Label
from elements.vbox import VBox
from screens.recharge_screen import RechargeScreen
from users.users import Users
from .confirm_payment_screen import ConfirmPaymentScreen
from .id_card_screen import IDCardScreen
from .purchase_history_screen import PurchaseHistoryScreen
from .screen import Screen
from .screen_manager import ScreenManager
from .transfer_balance_screen import TransferBalanceScreen


class ProfileScreen(Screen):
    idle_timeout = 20

    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.processing = None
        self.drink_info = None
        self.zuordnen = None
        self.btn_abbrechen = None
        self.elements_aufladungen = []
        self.elements_drinks = []

    def on_start(self, *args, **kwargs):
        self.objects = [
            Label(
                text=self.account.name,
                pos=(5, 5),
            ),
            VBox(
                [
                    Label(
                        text="Guthaben",
                        size=20,
                    ),
                    Label(
                        text=f"{self.account.balance} €",
                        size=40,
                    ),
                ],
                pos=(config.SCREEN_WIDTH - 5, 5),
                align_right=True,
            ),
            VBox(
                [
                    Label(
                        text="Scanne eine",
                        size=50,
                    ),
                    Label(
                        text="Flasche",
                        size=50,
                    ),
                    Label(text="oder wähle:", size=25),
                ],
                pos=(5, 100),
            ),
            VBox(
                [
                    Button(
                        text="Buchungshistorie",
                        on_click=lambda: self.goto(PurchaseHistoryScreen(self.account)),
                        padding=20,
                    ),
                    Button(
                        text="Aufladen",
                        on_click=lambda: self.goto(RechargeScreen(self.account)),
                        padding=20,
                    ),
                    Button(
                        text="Guthaben übertragen",
                        on_click=lambda: self.goto(TransferBalanceScreen(self.account)),
                        padding=20,
                    ),
                    Button(
                        text="ID card",
                        font=Font.MONOSPACE,
                        on_click=lambda: self.goto(IDCardScreen(self.account)),
                        padding=20,
                    ),
                ],
                pos=(5, 300),
                gap=15,
            ),
            # Image(
            #     src="drinks_touch/resources/images/new-text.png",
            #     pos=(330, 370),
            # ),
        ]

        self.processing = Label(
            text="Moment bitte...",
            size=20,
            pos=(150, 750),
        )
        self.processing.visible = False
        self.objects.append(self.processing)

        drink = DrinksManager.instance.get_selected_drink()
        self.drink_info = Label(
            text=drink["name"] if drink else "",
            size=30,
            pos=(30, 580),
        )

        if drink:
            self.goto(ConfirmPaymentScreen(self.account, drink))
            # self.objects.extend([self.zuordnen, self.drink_info])
        return

        self.render_aufladungen()

    def render_aufladungen(self):
        # aufladungen = Users.get_recharges(self.user["id"], limit=12)
        aufladungen = self.account.get_recharges().limit(12).all()
        y = 210
        prev_date = None
        for i, aufladung in enumerate(aufladungen):
            x = 30
            if y + 45 * 2 >= self.btn_drinks.pos[1]:
                self.elements_aufladungen.append(Label(text="...", pos=(x, y)))
                break
            date = aufladung.timestamp.strftime("%a, %-d.%-m.%Y")
            time = aufladung.timestamp.strftime("%H:%M")
            time_text = time
            helper = aufladung.helper_user_id
            if helper:
                if helper == "SEPA":
                    time_text += " mit SEPA"
                elif helper == "DISPLAY":
                    time_text += " mit DISPLAY"
                else:
                    # TODO: this is the slow part because it queries LDAP
                    user = Users.get_by_id(aufladung.helper_user_id)
                    if user:
                        helper = user["name"]
                        time_text += " mit " + helper
            if date != prev_date:
                prev_date = date
                self.elements_aufladungen.append(
                    Label(text=date, size=30, pos=(x, y + 15))
                )
                y += 45
            count_width = 120
            margin_right = 10
            self.elements_aufladungen.append(
                Label(
                    text=time_text,
                    pos=(x + 10, y),
                    size=25,
                    max_width=480 - x - margin_right - count_width,
                )
            )
            self.elements_aufladungen.append(
                Label(
                    text=str(aufladung.amount),
                    align_right=True,
                    pos=(480 - margin_right, y - 5),
                    max_width=count_width,
                    size=25,
                )
            )
            y += 35

    def on_barcode(self, barcode):
        if not barcode:
            return
        self.processing.text = f"Gescannt: {barcode}"
        self.processing.visible = True
        account = Account.query.filter(Account.id_card == barcode).first()
        if account:
            ScreenManager.instance.set_active(ProfileScreen(account))
            self.processing.visible = False
            return
        drink = get_by_ean(barcode)
        DrinksManager.instance.set_selected_drink(drink)
        if drink:
            self.goto(ConfirmPaymentScreen(self.account, drink))
        self.drink_info.text = drink["name"]
        self.processing.visible = False

    def show_aufladungen(self):
        for d in self.elements_drinks:
            self.objects.remove(d)
        self.objects.extend(self.elements_aufladungen)

    def show_drinks(self):
        for d in self.elements_aufladungen:
            self.objects.remove(d)
        self.objects.extend(self.elements_drinks)
