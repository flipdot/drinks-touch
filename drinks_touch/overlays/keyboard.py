import enum

import pygame
from pygame.event import EventType

from elements import Label
from elements.base_elm import BaseElm
from overlays import BaseOverlay
from screens.screen_manager import ScreenManager


class KeyboardLayout(enum.Enum):
    DEFAULT = "default"
    NUMERIC = "numeric"


class KeyboardOverlay(BaseOverlay):
    ANIMATION_DURATION = 0.2

    def __init__(self, screen_manager: ScreenManager):
        super().__init__(screen_manager)
        self.width = self.screen.get_width()
        self.height = 350
        self.pos = pygame.Vector2(
            0,
            self.screen.get_height()
            - self.height
            - self.screen_manager.MENU_BAR_HEIGHT,
        )

        self._anim_start_pos = pygame.Vector2(
            0, self.screen.get_height() - self.height * 0.9
        )
        self.objects: list[BaseElm] = [
            Label(
                text="Keyboard",
                pos=(0, 0),
            )
        ]
        self.clock = 0

    def render(self, dt):
        if not self.visible:
            self.clock = 0
            return
        self.clock += dt
        surface = pygame.Surface(
            (self.screen.get_width(), self.height), pygame.SRCALPHA
        )
        surface.fill((0, 0, 0, 255))

        for obj in self.objects:
            obj_surface = obj.render(dt)
            if obj_surface is not None:
                surface.blit(obj_surface, obj.screen_pos)

        # full alpha (255) after ANIMATION_DURATION
        alpha = min(255, int((self.clock / self.ANIMATION_DURATION) * 255))
        surface.set_alpha(alpha)

        # self.pos after ANIMATION_DURATION, interpolate
        # from self._anim_start_pos to self.pos
        if self.clock < self.ANIMATION_DURATION:
            pos = self._anim_start_pos.lerp(
                self.pos, self.clock / self.ANIMATION_DURATION
            )
        else:
            pos = self.pos

        self.screen.blit(surface, pos)
        # self.tick += dt
        # self._render_click_animation()
        # self._render_mouse_path()
        # self._render_mouse_pos()

    def events(self, events: list[EventType]):
        if not self.visible:
            return False
        # check if click is inside keyboard
        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                or event.type == pygame.MOUSEBUTTONUP
            ):
                transformed_pos = (
                    event.pos[0] - self.pos[0],
                    event.pos[1] - self.pos[1],
                )
                if self.collides_with(transformed_pos):
                    event.dict["consumed"] = True
                    for obj in self.objects[::-1]:
                        if consumed_by := obj.event(event, transformed_pos):
                            return consumed_by

    def collides_with(self, pos: tuple[float, float]) -> bool:
        return pygame.Rect(0, 0, self.width, self.height).collidepoint(pos[0], pos[1])

    @property
    def visible(self):
        if obj := self.screen_manager.active_object:
            return obj.keyboard_settings["enabled"]
