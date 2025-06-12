import pygame
from pygame.mixer import Sound

import config
from config import Color
from database.models import Account
from elements import Button
from elements.base_elm import BaseElm
from elements.hbox import HBox
from elements.label import Label
from elements.vbox import VBox
from notifications.notification import send_drink
from .screen import Screen
from .tetris.constants import SPRITE_RESOLUTION
from .tetris.screen import TetrisScreen, Shape, BlockType


class TetrisIcon(BaseElm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scale = 1.5
        self.shape = Shape(BlockType.T)

    @property
    def width(self):
        return SPRITE_RESOLUTION.x * self.scale * 3

    @property
    def height(self):
        return SPRITE_RESOLUTION.y * self.scale * 2

    def _render(self, *args, **kwargs) -> pygame.Surface:
        return self.shape.render(Color.PRIMARY.value)


class SuccessScreen(Screen):
    idle_timeout = 10

    def __init__(self, account: Account, drink, text, offer_games: bool = False):
        super().__init__()

        self.account = account
        self.text = text
        self.drink = drink
        self.offer_games = offer_games

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
                    Label(text="Danke!", size=70),
                    Label(text=self.text, size=20),
                ],
                pos=(5, 100),
            ),
            Button(
                text="Nein Danke",
                on_click=self.home,
                size=50,
                pos=(80, config.SCREEN_HEIGHT - 100),
                align_bottom=True,
            ),
        ]

        if self.offer_games:
            self.objects.extend(
                [
                    Button(
                        inner=HBox(
                            [
                                TetrisIcon(),
                                Label(
                                    text="einen Stein setzen",
                                    size=30,
                                    padding=(5, 10, 0),
                                ),
                            ]
                        ),
                        on_click=lambda: self.goto(TetrisScreen(self.account)),
                        size=20,
                        pos=(40, config.SCREEN_HEIGHT - 300),
                    ),
                ]
            )

        self.play_sound()

        if self.drink:
            send_drink(self.account, self.drink)

    def event(self, event) -> BaseElm | None:
        if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            if self.offer_games:
                self.goto(TetrisScreen(self.account))
            else:
                self.home()
        else:
            return super().event(event)

    def play_sound(self):
        balance = self.account.balance
        if balance >= 0:
            filename = "smb_coin.wav"
        elif balance < -10:
            filename = "alarm.wav"
        else:
            filename = "smb_bowserfalls.wav"

        # local sound
        Sound(f"drinks_touch/resources/sounds/{filename}").play()

        # remote sound - remote pi currently not available
        # os.system(
        #     "ssh -o StrictHostKeyChecking=no pi@pixelfun aplay sounds/%s >/dev/null 2>&1 &"
        #     % filename
        # )
