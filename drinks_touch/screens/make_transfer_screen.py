import math
from decimal import Decimal
from enum import Enum

import pygame
from pygame import Vector2
from pygame.mixer import Sound

import config
from database.models import Account, RechargeEvent, Tx
from database.storage import Session
from elements import Label, Animation, Image
from elements.base_elm import BaseElm
from elements.spacer import Spacer
from elements.vbox import VBox
from screens.screen import Screen
from screens.screen_manager import ScreenManager


class AnimationPhase(Enum):
    WALK_IN = 1
    JUMP_UP = 2
    JUMP_DOWN = 3
    STAND = 4
    WALK_OUT = 5


class MakeTransferScreen(Screen):
    MARIO_SIZE = Vector2(16, 16) * 5
    Q_BOX_SIZE = MARIO_SIZE
    COIN_SIZE = Q_BOX_SIZE
    DURATIONS = {
        AnimationPhase.WALK_IN: 2,
        AnimationPhase.JUMP_UP: 0.3,
        AnimationPhase.JUMP_DOWN: 0.3,
        AnimationPhase.STAND: 0.05,
        AnimationPhase.WALK_OUT: 2,
    }

    nav_bar_visible = False

    def __init__(self, account: Account, to_account: Account, amount: Decimal):
        super().__init__()
        self.account = account
        self.to_account = to_account
        if not isinstance(amount, Decimal):
            raise ValueError("Amount must be a Decimal")
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        self.amount = amount
        self.balance_from = account.balance
        self.balance_to = to_account.balance

        self._transfer_balance()

        self.clock = 0
        self.jump_counter = 0
        self.mario_start_pos = Vector2(-100, config.SCREEN_HEIGHT - 100)
        self.mario_pos = self.mario_start_pos
        self.mario_jump_start_pos = Vector2(
            config.SCREEN_WIDTH / 2 - self.MARIO_SIZE.x / 2, self.mario_pos.y
        )
        self.q_box_start_pos = Vector2(
            config.SCREEN_WIDTH / 2 - self.Q_BOX_SIZE.x / 2,
            self.mario_pos.y - self.MARIO_SIZE.y * 3,
        )
        self.q_box_pos = self.q_box_start_pos
        self.coin_start_pos = self.q_box_start_pos - Vector2(0, self.Q_BOX_SIZE.y)
        self.coin_pos = self.coin_start_pos
        self.animation_mario_walk = Animation(
            "drinks_touch/resources/images/mario/walk/frame{0}.png",
            n_frames=3,
            size=self.MARIO_SIZE,
            pos=self.mario_pos,
            scale_smooth=False,
        )
        self.animation_coin = Animation(
            "drinks_touch/resources/images/coin/frame{0}.png",
            n_frames=4,
            size=self.COIN_SIZE,
            pos=self.coin_pos,
            visible=False,
            scale_smooth=False,
        )
        self.mario_jump = Image(
            "drinks_touch/resources/images/mario/jump.png",
            size=self.MARIO_SIZE,
            pos=self.mario_pos,
            visible=False,
            scale_smooth=False,
        )
        self.mario_stand = Image(
            "drinks_touch/resources/images/mario/stand.png",
            size=self.MARIO_SIZE,
            pos=self.mario_pos,
            visible=False,
            scale_smooth=False,
        )
        self.q_box_on = Image(
            "drinks_touch/resources/images/q_box/on.png",
            size=self.Q_BOX_SIZE,
            pos=self.q_box_start_pos,
            scale_smooth=False,
        )
        self.q_box_off = Image(
            "drinks_touch/resources/images/q_box/off.png",
            size=self.Q_BOX_SIZE,
            pos=self.q_box_start_pos,
            scale_smooth=False,
            visible=False,
        )
        self.label_amount_from = Label(
            text=f"{self.balance_from:.2f} €",
        )
        self.label_amount_to = Label(
            text=f"{self.balance_to:.2f} €",
        )
        self.animation_phase = AnimationPhase.WALK_IN
        self.sound_coin = Sound("drinks_touch/resources/sounds/smb_coin.wav")

    def _transfer_balance(self):
        session = Session()
        positive_charge = Tx(
            payment_reference=f"Übertrag von {self.account.name}",
            account_id=self.to_account.id,
            amount=self.amount,
        )
        negative_charge = Tx(
            payment_reference=f"Übertrag an {self.to_account.name}",
            account_id=self.account.id,
            amount=-self.amount,
        )
        session.add(positive_charge)
        session.add(negative_charge)
        session.flush()
        positive_charge_event = RechargeEvent(
            self.to_account.ldap_id,
            self.account.name,
            self.amount,
            tx_id=positive_charge.id,
        )
        negative_charge_event = RechargeEvent(
            self.account.ldap_id,
            self.to_account.name,
            -self.amount,
            tx_id=negative_charge.id,
        )
        session.add(negative_charge_event)
        session.add(positive_charge_event)
        session.commit()

    def on_start(self, *args, **kwargs):
        self.objects = [
            Label(
                text=self.account.name,
                pos=(5, 5),
            ),
            VBox(
                [
                    self.label_amount_from,
                    Label(
                        text=self.account.name,
                        size=20,
                    ),
                ],
                pos=(25, config.SCREEN_HEIGHT / 2 - 50),
            ),
            Spacer(width=20),
            VBox(
                [
                    self.label_amount_to,
                    Label(
                        text=self.to_account.name,
                        size=20,
                    ),
                ],
                pos=(config.SCREEN_WIDTH - 25, config.SCREEN_HEIGHT / 2 - 50),
                align_right=True,
            ),
            self.animation_mario_walk,
            self.mario_jump,
            self.mario_stand,
            self.q_box_on,
            self.q_box_off,
            self.animation_coin,
        ]

    def event(self, event) -> BaseElm | None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            ScreenManager.instance.set_default()
            return None
        return super().event(event)

    def tick(self, dt):
        super().tick(dt)
        self.clock += dt

    def render(self):
        if self.clock > self.DURATIONS[self.animation_phase]:
            if self.animation_phase == AnimationPhase.WALK_OUT:
                ScreenManager.instance.set_default()
                return None, None
            self.animation_phase = AnimationPhase(self.animation_phase.value + 1)
            self.clock = 0
            if (
                self.animation_phase == AnimationPhase.WALK_OUT
                and self.jump_counter < self.amount
            ):
                self.animation_phase = AnimationPhase.JUMP_UP
            if self.animation_phase == AnimationPhase.JUMP_UP:
                self.animation_mario_walk.visible = False
                self.mario_stand.visible = False
                self.mario_jump.visible = True
                self.q_box_pos = self.q_box_start_pos
            elif self.animation_phase == AnimationPhase.JUMP_DOWN:
                self.jump_counter += 1
                self.balance_from -= 1
                self.balance_to += 1
                if self.jump_counter >= self.amount:
                    self.q_box_on.visible = False
                    self.q_box_off.visible = True
                    diff = Decimal(self.jump_counter) - self.amount
                    self.balance_from += diff
                    self.balance_to -= diff

                self.label_amount_from.text = f"{self.balance_from:.2f} €"
                self.label_amount_to.text = f"{self.balance_to:.2f} €"
                self.animation_coin.visible = True
                self.coin_pos = self.coin_start_pos
                self.sound_coin.play()
            elif self.animation_phase == AnimationPhase.STAND:
                self.mario_jump.visible = False
                self.mario_stand.visible = True
                self.q_box_pos = self.q_box_start_pos
                self.animation_coin.visible = False
            elif self.animation_phase == AnimationPhase.WALK_OUT:
                self.mario_stand.visible = False
                self.mario_jump.visible = False
                self.animation_mario_walk.visible = True

        if self.animation_phase == AnimationPhase.WALK_IN:
            self.animation_walk_in()
        elif self.animation_phase == AnimationPhase.JUMP_UP:
            self.animation_jump_up()
        elif self.animation_phase == AnimationPhase.JUMP_DOWN:
            self.animation_jump_down()
        elif self.animation_phase == AnimationPhase.WALK_OUT:
            self.animation_walk_out()

        self.mario_jump.pos = self.mario_pos
        self.animation_mario_walk.pos = self.mario_pos
        self.mario_stand.pos = self.mario_pos
        self.q_box_on.pos = self.q_box_pos
        self.q_box_off.pos = self.q_box_pos
        self.animation_coin.pos = self.coin_pos

        return super().render()

    def animation_walk_in(self):
        self.mario_pos = self.mario_start_pos.lerp(
            self.mario_jump_start_pos,
            self.clock / self.DURATIONS[AnimationPhase.WALK_IN],
        )

    def animation_jump_up(self):
        to_pos = self.q_box_start_pos + Vector2(0, self.Q_BOX_SIZE.y)
        self.mario_pos = self.mario_jump_start_pos.lerp(
            to_pos,
            math.sin(
                math.pi * 0.5 * self.clock / self.DURATIONS[AnimationPhase.JUMP_UP]
            ),
        )

    def animation_jump_down(self):
        from_pos = self.q_box_start_pos + Vector2(0, self.Q_BOX_SIZE.y)
        self.mario_pos = from_pos.lerp(
            self.mario_jump_start_pos,
            1
            - math.cos(
                math.pi * 0.5 * self.clock / self.DURATIONS[AnimationPhase.JUMP_DOWN]
            ),
        )

        coin_to_pos = self.coin_start_pos - Vector2(0, self.COIN_SIZE.y * 3)

        self.coin_pos = self.coin_start_pos.lerp(
            coin_to_pos,
            self.clock / self.DURATIONS[AnimationPhase.JUMP_DOWN],
        )

        # Within the duration that mario needs to reach the ground,
        # the ?-Block should jump up half of its height and then fall back
        # down to its original position

        q_box_up_pos = self.q_box_start_pos - Vector2(0, self.Q_BOX_SIZE.y / 2)

        top_reached_at = self.DURATIONS[AnimationPhase.JUMP_DOWN] / 3
        bottom_reached_at = self.DURATIONS[AnimationPhase.JUMP_DOWN] / 3 * 2

        if self.clock < top_reached_at:
            self.q_box_pos = self.q_box_start_pos.lerp(
                q_box_up_pos,
                math.sin(math.pi * 0.5 * self.clock / top_reached_at),
            )
        elif self.clock < bottom_reached_at:
            self.q_box_pos = q_box_up_pos.lerp(
                self.q_box_start_pos,
                1
                - math.cos(
                    math.pi
                    * 0.5
                    * (self.clock - top_reached_at)
                    / (bottom_reached_at - top_reached_at)
                ),
            )

    def animation_walk_out(self):
        self.mario_pos = self.mario_jump_start_pos.lerp(
            Vector2(config.SCREEN_WIDTH + 100, self.mario_jump_start_pos.y),
            self.clock / self.DURATIONS[AnimationPhase.WALK_OUT],
        )
