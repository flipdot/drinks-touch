from itsdangerous import TimedSerializer

import config
from config import Color
from database.models import Account
from database.storage import with_db
from elements import Label, Button, SvgIcon
from elements.hbox import HBox
from elements.vbox import VBox
from notifications.notification import send_notification, render_jinja_template
from screens.screen import Screen


class EnableTransactionHistoryScreen(Screen):

    def __init__(self, account: Account):
        super().__init__()

        self.account = account

    @with_db
    def on_start(self, *args, **kwargs):
        if self.account.tx_history_visible:
            self.back()
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
                    HBox(
                        [
                            Label(
                                text="Datum",
                                size=24,
                                width=100,
                                color=Color.PRIMARY_DARK,
                            ),
                            Label(
                                text="Referenz",
                                size=24,
                                width=280,
                                color=Color.PRIMARY_DARK,
                            ),
                            Label(
                                text="Betrag",
                                size=24,
                                width=160,
                                color=Color.PRIMARY_DARK,
                            ),
                        ]
                    ),
                    HBox(
                        width=config.SCREEN_WIDTH - 10,
                        height=1,
                        bg_color=Color.PRIMARY_DARK,
                    ),
                ],
                pos=(5, 90),
            ),
            VBox(
                [
                    Label(text="Die Transaktionshistorie ist"),
                    Label(text="standardmäßig verborgen."),
                    Label(text="Sie existiert jedoch, der"),
                    Label(text="drinks-touch ist leider noch"),
                    Label(text="nicht datensparsam genug."),
                    Label(text=""),
                    Label(text="Um dir ein bisschen Privat-"),
                    Label(text="sphäre zu geben, musst du"),
                    Label(text="diesen Screen via E-Mail"),
                    Label(text="aktivieren."),
                ],
                pos=(5, 150),
            ),
            Button(
                inner=HBox(
                    [
                        SvgIcon(
                            "drinks_touch/resources/images/unlock.svg",
                            width=40,
                            color=Color.PRIMARY,
                        ),
                        Label(text="Freischalten"),
                    ]
                ),
                pos=(100, 650),
                on_click=self.enable_transaction_history,
            ),
        ]

    @with_db
    def enable_transaction_history(self):
        signer = TimedSerializer(config.SECRET_KEY, salt="enable_transaction_history")
        signed_account_id = signer.dumps(self.account.id)
        url = f"{config.BASE_URL}/enable_transaction_history/{signed_account_id}"

        context = {
            "username": self.account.name,
            "url": url,
        }
        content_html = render_jinja_template(
            "enable_transaction_history.html", **context
        )
        content_text = render_jinja_template(
            "enable_transaction_history.txt", **context
        )

        send_notification(
            self.account.email,
            "Freischaltung Transaktionshistorie",
            content_text,
            content_html,
            self.account.ldap_id,
        )
        self.alert("E-Mail wurde versendet")
