import pygame

import config
from config import Color
from elements.base_elm import BaseElm
from screen import get_screen_surface
from screens.screen_manager import ScreenManager


class Screen:

    idle_timeout = 10

    def __init__(self, width=None, height=None):
        if width is None or height is None:
            screen_surface = get_screen_surface()
            width = width or screen_surface.get_width()
            height = height or screen_surface.get_height()
        self.width = width
        self.height = height
        self.objects: list[BaseElm] = []
        self.on_create()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def render(self, dt):
        surface = pygame.Surface((self.width, self.height))
        surface.fill(Color.BACKGROUND.value)
        if config.DEBUG_UI_ELEMENTS:
            debug_surface = pygame.Surface((self.width, self.height))
        else:
            debug_surface = None
        for o in self.objects:
            if o.visible:
                obj_surface = o.render(dt)
                if obj_surface is not None:
                    surface.blit(obj_surface, o.screen_pos)
                if config.DEBUG_UI_ELEMENTS:
                    obj_debug_surface = o.render_debug()
                    if obj_debug_surface is not None:
                        debug_surface.blit(obj_debug_surface, o.screen_pos)
        return surface, debug_surface

    def event(self, event):
        for obj in self.objects[::-1]:
            if getattr(event, "consumed", False):
                break
            obj.event(event)

    @staticmethod
    def back():
        ScreenManager.get_instance().go_back()

    @staticmethod
    def goto(screen: "Screen", *args, **kwargs):
        ScreenManager.get_instance().set_active(screen, *args, **kwargs)

    # lifecycle inspired by https://developer.android.com/guide/components/activities/activity-lifecycle
    # Not all yet implemented

    def on_create(self, *args, **kwargs):
        pass

    def on_start(self, *args, **kwargs):
        pass

    # def on_resume(self):
    #     pass

    # def on_pause(self):
    #     pass

    def on_stop(self, *args, **kwargs):
        pass

    def on_destroy(self, *args, **kwargs):
        pass
