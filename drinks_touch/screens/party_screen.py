from pathlib import Path

import pygame
from sqlalchemy import select, insert

import config
from database.models import Account, TetrisPlayer
from database.storage import Session, with_db
from elements import SvgIcon, Label, Button
from elements.hbox import HBox
from screens.screen import Screen
from screens.success import TetrisIcon
from screens.tetris.screen import TetrisScreen


class PartyScreen(Screen):
    idle_timeout = 60000

    @with_db
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        query = select(Account).filter(Account.name == "recharge")
        self.account = Session().execute(query).scalar_one_or_none()
        if not self.account:
            Session().execute(insert(Account).values(name="recharge"))
            self.account = Session().execute(query).scalar_one()
            Session().execute(
                insert(TetrisPlayer).values(
                    account_id=self.account.id,
                    color="#FF6633",
                )
            )
        self.hexagon = SvgIcon.load_image(
            Path("drinks_touch/resources/images/recharge/hexagon.svg"), width=400
        )
        self.battery = SvgIcon.load_image(
            Path("drinks_touch/resources/images/recharge/battery.svg"), width=400
        )
        self.thunderbolt = SvgIcon.load_image(
            Path("drinks_touch/resources/images/recharge/thunderbolt.svg"), width=400
        )
        self.text = SvgIcon.load_image(
            Path("drinks_touch/resources/images/recharge/text.svg"), width=400
        )
        self.ts = 0

        self.hexagon_rotation = 0
        self.zoom = 1
        self.increase_zoom = False
        self.zoom_change_rate = 0

        self.jump_animation_started_at = 0

    @with_db
    def on_start(self, *args, **kwargs):
        self.objects = [
            # SvgIcon(
            #     "drinks_touch/resources/images/mate.svg",
            #     width=config.SCREEN_WIDTH / 2,
            #     pos=(config.SCREEN_WIDTH / 4, 20),
            #     color=config.Color.PRIMARY,
            # ),
            # SvgIcon(
            #     "drinks_touch/resources/images/recharge.svg",
            #     width=400,
            #     pos=(40, 180),
            # ),
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
                pos=(40, config.SCREEN_HEIGHT - 200),
            ),
        ]

    def on_barcode(self, barcode):
        self.goto(TetrisScreen(self.account))

    def tick(self, dt: float):
        super().tick(dt)
        self.ts += dt
        self.hexagon_rotation = (self.hexagon_rotation - dt * 3) % 360

        if self.increase_zoom:
            self.zoom_change_rate = 200

        self.zoom = round(max(-500, min(500, self.zoom + dt * self.zoom_change_rate)))

        if self.zoom > 1:
            if self.zoom_change_rate > 0:
                self.zoom_change_rate = round(self.zoom_change_rate * 0.9)
            else:
                self.zoom_change_rate = round(self.zoom_change_rate * 1.1)

        elif self.zoom < 1:
            if self.zoom_change_rate < 0:
                self.zoom_change_rate = round(self.zoom_change_rate * 0.9)
            else:
                self.zoom_change_rate = round(self.zoom_change_rate * 1.1)

        if self.zoom_change_rate > 0:
            self.zoom_change_rate -= 1
        elif self.zoom_change_rate < 0:
            self.zoom_change_rate += 1
        #
        # # print(f"zoom_change_rate: {self.zoom_change_rate}")
        # # print(f"zoom: {self.zoom}")
        #
        if self.zoom_change_rate == 0:
            if self.zoom > 1:
                self.zoom_change_rate = -20
            elif self.zoom < 1:
                self.zoom_change_rate = 20

        # print(self.zoom_change_rate)

        # Adjust the change rate, so that the zoom is always moving towards 1.
        # The further away from 1, the faster it moves.
        # if self.zoom > 1:
        #     self.zoom_change_rate = self.zoom_change_rate - dt * 2000
        #     # self.zoom_change_rate = -50 - (self.zoom - 1) * 2
        # elif self.zoom < 1:
        #     self.zoom_change_rate = self.zoom_change_rate + dt * 2000
        #     # self.zoom_change_rate = 50 + (1 - self.zoom) * 2
        # else:
        #     self.zoom_change_rate = 0

        # if self.zoom > 1 and self.zoom_change_rate == 0:
        #     self.zoom_change_rate
        # else:
        #     self.zoom = max(1, self.zoom - dt * 5)

        # if (self.ts - self.jump_animation_started_at) * 5 > math.pi:
        #     self.zoom = 1
        # else:
        #     self.zoom = (
        #         1 + math.sin((self.ts - self.jump_animation_started_at) * 5) * 200
        #     )

    def _render(self) -> tuple[pygame.Surface, pygame.Surface | None]:
        surface, debug_surface = super()._render()
        # draw hexagon
        hexagon_zoom = self.zoom * -0.3
        hexagon_pos = (40, 180)
        hexagon_size = (
            max(0, self.hexagon.get_width() + hexagon_zoom),
            max(0, self.hexagon.get_height() + hexagon_zoom),
        )
        scaled_hexagon = pygame.transform.scale(
            self.hexagon, (int(hexagon_size[0]), int(hexagon_size[1]))
        )
        rotated_hexagon = pygame.transform.rotate(scaled_hexagon, self.hexagon_rotation)
        hexagon_rect = rotated_hexagon.get_rect(
            center=(
                hexagon_pos[0] + self.hexagon.get_width() // 2,
                hexagon_pos[1] + self.hexagon.get_height() // 2,
            )
        )
        surface.blit(rotated_hexagon, hexagon_rect.topleft)

        # draw battery
        battery_zoom = self.zoom * 0.5
        battery_pos = (40, 180)
        battery_size = (
            max(0, self.battery.get_width() + battery_zoom),
            max(0, self.battery.get_height() + battery_zoom),
        )
        scaled_battery = pygame.transform.scale(
            self.battery, (int(battery_size[0]), int(battery_size[1]))
        )
        battery_rect = scaled_battery.get_rect(
            center=(
                battery_pos[0] + self.battery.get_width() // 2,
                battery_pos[1] + self.battery.get_height() // 2,
            )
        )
        surface.blit(scaled_battery, battery_rect.topleft)

        # draw thunderbolt
        thunderbolt_zoom = self.zoom * 0.9
        thunderbolt_pos = (40, 180)
        thunderbolt_size = (
            max(0, self.thunderbolt.get_width() + thunderbolt_zoom),
            max(0, self.thunderbolt.get_height() + thunderbolt_zoom),
        )
        scaled_thunderbolt = pygame.transform.scale(
            self.thunderbolt, (int(thunderbolt_size[0]), int(thunderbolt_size[1]))
        )
        thunderbolt_rect = scaled_thunderbolt.get_rect(
            center=(
                thunderbolt_pos[0] + self.thunderbolt.get_width() // 2,
                thunderbolt_pos[1] + self.thunderbolt.get_height() // 2,
            )
        )
        surface.blit(scaled_thunderbolt, thunderbolt_rect.topleft)

        # draw text
        text_size = self.zoom * 0.4
        text_pos = (40, 180)
        scaled_text = pygame.transform.scale(
            self.text,
            (
                max(0, int(self.text.get_width() + text_size)),
                max(0, int(self.text.get_height() + text_size)),
            ),
        )
        text_rect = scaled_text.get_rect(
            center=(
                text_pos[0] + self.text.get_width() // 2,
                text_pos[1] + self.text.get_height() // 2,
            )
        )
        surface.blit(scaled_text, text_rect.topleft)
        return surface, debug_surface

    def calculate_hash(self):
        super_hash = super().calculate_hash()
        return hash(
            (
                super_hash,
                self.hexagon_rotation,
                self.zoom,
            )
        )

    def event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.increase_zoom = True
            # self.jump_animation_started_at = self.ts
        elif event.type == pygame.MOUSEBUTTONUP:
            self.increase_zoom = False
            # self.jump_animation_started_at = self.ts
        return super().event(event)
