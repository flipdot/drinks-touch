from pygame.event import EventType

from screen import get_screen_surface

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.screen_manager import ScreenManager


class BaseOverlay:
    def __init__(self, screen_manager: "ScreenManager"):
        self.screen = get_screen_surface()
        self.screen_manager = screen_manager

    def render(self, dt):
        pass

    def events(self, events: list[EventType]):
        pass
