import math
from decimal import Decimal
from enum import Enum

from pygame import Vector2

import config
from database.models import Account
from elements import Label, Animation, Image
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
        self.amount = amount

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
        self.animation_mario_walk = Animation(
            "drinks_touch/resources/images/mario/walk/frame{0}.png",
            n_frames=3,
            size=self.MARIO_SIZE,
            pos=self.mario_pos,
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
        self.animation_phase = AnimationPhase.WALK_IN

    def on_start(self, *args, **kwargs):
        self.objects = [
            Label(
                text=self.account.name,
                pos=(5, 5),
            ),
            self.animation_mario_walk,
            self.mario_jump,
            self.mario_stand,
            self.q_box_on,
            self.q_box_off,
        ]

    def render(self, dt):
        self.clock += dt

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
                self.jump_counter += 1
            elif self.animation_phase == AnimationPhase.JUMP_DOWN:
                if self.jump_counter >= self.amount:
                    self.q_box_on.visible = False
                    self.q_box_off.visible = True
            elif self.animation_phase == AnimationPhase.STAND:
                self.mario_jump.visible = False
                self.mario_stand.visible = True
                self.q_box_pos = self.q_box_start_pos
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

        return super().render(dt)

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
