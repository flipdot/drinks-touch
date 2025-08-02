import logging
from io import BytesIO

import pygame
from sqlalchemy import select, func

import config
from config import Color
from database.models import Account, Tx
from database.storage import with_db, Session
from elements import Label
from elements.vbox import VBox
from screens.screen import Screen
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


logger = logging.getLogger(__name__)

# logger.setLevel(logging.DEBUG)


def to_mpl_color(color: Color) -> tuple[float, float, float]:
    rgba = color.value  # (r, g, b, a)
    return tuple(c / 255 for c in rgba[:3])  # Only RGB for matplotlib


class TransactionHistoryStatsScreen(Screen):
    def __init__(self, account: Account):
        super().__init__()

        self.account = account
        self.graph_surface: pygame.Surface | None = None

    @with_db
    def on_start(self, *args, **kwargs):
        if not self.account.tx_history_visible:
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
        ]
        self.graph_surface = self.plot_account_balance()

    def _render(self):
        surface, debug_surface = super()._render()
        if self.graph_surface:
            surface.blit(self.graph_surface, (5, 100))
        return surface, debug_surface

    @with_db
    def plot_account_balance(self) -> pygame.Surface:

        stmt = (
            select(
                func.date_trunc("month", Tx.created_at).label("month"),
                func.sum(Tx.amount).label("summed"),
            )
            .where(Tx.account_id == self.account.id)
            .group_by(func.date_trunc("month", Tx.created_at))
            .order_by("month")
        )

        logger.debug("Executing SQL statement to fetch transaction data")
        transactions = Session().execute(stmt).all()
        logger.debug(f"Fetched {len(transactions)} transactions")

        # Build a DataFrame and compute cumulative balance
        logger.debug("Building DataFrame for plotting")
        df = pd.DataFrame(transactions, columns=["timestamp", "amount"])
        logger.debug("Calculating cumulative balance")
        df["balance"] = df["amount"].cumsum()

        bg_color = to_mpl_color(Color.BACKGROUND)
        text_color = to_mpl_color(Color.PRIMARY)

        # Plotting
        logger.debug("Creating plot")
        fig, ax = plt.subplots(
            figsize=(
                (config.SCREEN_WIDTH - 10) / 100,
                (config.SCREEN_HEIGHT - 170) / 100,
            )
        )

        # Set background
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        # Set axes and text colors
        ax.tick_params(colors=text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)
        for spine in ax.spines.values():
            spine.set_color(text_color)

        # Fill green where balance is positive, red when negative
        for i in range(1, len(df)):
            prev = df.iloc[i - 1]
            curr = df.iloc[i]
            x = [prev["timestamp"], curr["timestamp"]]
            y = [prev["balance"], curr["balance"]]
            color = "green" if prev["balance"] >= 0 else "red"
            ax.plot(x, y, color=color)
            ax.fill_between(
                x, y, 0, where=[b >= 0 for b in y], color="green", alpha=0.3
            )
            ax.fill_between(x, y, 0, where=[b < 0 for b in y], color="red", alpha=0.3)

        # Format the x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)

        ax.text(
            -0.01,
            1.01,
            "Betrag (€)",
            ha="center",
            va="bottom",
            transform=ax.transAxes,
            color=text_color,
        )
        plt.tight_layout()
        buf = BytesIO()
        logger.debug("Saving plot to buffer")
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        logger.debug("Converting buffer to pygame surface")
        return pygame.image.load(buf, "balance_graph.png")

    @with_db
    def count_transactions(self) -> int:
        query = select(func.count(Tx.id)).where(Tx.account_id == self.account.id)
        return Session().execute(query).scalar()
