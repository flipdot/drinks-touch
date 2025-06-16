from pygame.event import EventType

from screen import get_screen_surface

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.screen_manager import ScreenManager


class BaseOverlay:
    def __init__(self, screen_manager: "ScreenManager"):
        self.screen = get_screen_surface()
        self.screen_manager = screen_manager
        self.t = 0.0

    def tick(self, dt: float):
        self.t += dt

    def render(self):
        pass

    def events(self, events: list[EventType]):
        pass
