import threading

import pygame

import config

from screens.screen_manager import ScreenManager
from .base import BaseOverlay


class BackgroundOverlay(BaseOverlay):
    threads: list[tuple[threading.Thread, str]] = []
    spinner = ["⢎⡰", "⢎⡡", "⢎⡑", "⢎⠱", "⠎⡱", "⢊⡱", "⢌⡱", "⢆⡱"]

    def __init__(self, screen_manager: ScreenManager):
        super().__init__(screen_manager)

    def render(self):
        for i, (thread, name) in enumerate(BackgroundOverlay.threads):
            spinner = BackgroundOverlay.spinner[
                int(self.t * 10) % len(BackgroundOverlay.spinner)
            ]
            label = f"{name}… {spinner}"
            self._render_thread_label(label, i)

    def _render_thread_label(self, label: str, idx: int):
        font = pygame.font.Font(config.Font.SANS_SERIF.value, 16)
        text_surface = font.render(label, True, config.Color.PRIMARY.value)
        text_rect = text_surface.get_rect()

        surface = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 200))
        surface.blit(text_surface, (0, 0))
        text_rect.y = (text_rect.height + 3) * idx
        text_rect.x = config.SCREEN_WIDTH - text_rect.width
        self.screen.blit(surface, text_rect)

    def reset(self):
        self.t = 0

    def tick(self, dt: float):
        super().tick(dt)
        BackgroundOverlay.threads = [
            (thread, name)
            for thread, name in BackgroundOverlay.threads
            if thread.is_alive()
        ]

    @classmethod
    def run(cls, function: callable, label: str = ""):
        thread = threading.Thread(target=function)
        BackgroundOverlay.threads.append((thread, label))
        thread.daemon = True
        thread.start()
