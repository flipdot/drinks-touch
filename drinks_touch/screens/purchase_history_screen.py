from sqlalchemy import text

import config
from database.models import Account, ScanEvent
from database.storage import get_session
from drinks.drinks import get_by_ean
from elements import Label
from elements.vbox import VBox
from screens.screen import Screen


class PurchaseHistoryScreen(Screen):

    def __init__(self, account: Account):
        super().__init__()
        self.account = account

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
        ]

        drinks = self.get_stats(limit=12)
        for i, drinks in enumerate(drinks):
            x = 30
            if i == 11:
                self.objects.append(Label(text="...", pos=(x, 210 + (i * 35))))
                break
            ean_text = get_by_ean(drinks["name"])["name"]
            count_width = 80
            margin_right = 10
            self.objects.append(
                Label(
                    text=ean_text,
                    pos=(x, 210 + (i * 35)),
                    max_width=480 - x - margin_right - count_width,
                )
            )
            self.objects.append(
                Label(
                    text=str(drinks["count"]),
                    align_right=True,
                    pos=(480 - margin_right, 210 + (i * 35)),
                    max_width=count_width,
                )
            )

    def get_stats(self, limit=None):

        ScanEvent.query

        session = get_session()
        sql = text(
            """
            SELECT COUNT(*) as count, barcode as name
            FROM scanevent
            WHERE user_id = :userid
            GROUP BY barcode
            ORDER by count DESC
            LIMIT :limit
        """
        )
        result = (
            session.connection()
            .execute(sql, {"userid": self.account.ldap_id, "limit": limit})
            .fetchall()
        )

        return [{"count": x[0], "name": x[1]} for x in result]
