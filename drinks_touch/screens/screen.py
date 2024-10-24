import pygame

import config
from elements.base_elm import BaseElm
from screens.screen_manager import ScreenManager


class Screen(object):
    def __init__(self, screen):
        self.screen = screen
        self.objects: list[BaseElm] = []

    def render(self, dt):
        for o in self.objects:
            if o.visible:
                surface = o.render(dt)
                if surface is not None:
                    self.screen.blit(surface, o.screen_pos)
                if config.DEBUG_UI_ELEMENTS:
                    debug_surface = o.render_debug()
                    if debug_surface is not None:
                        self.screen.blit(debug_surface, o.screen_pos)

    def events(self, events):
        for obj in self.objects:
            obj.events(events)
            for event in events:
                if "consumed" in event.dict and event.consumed:
                    continue

                if event.type == pygame.MOUSEBUTTONUP:
                    if not hasattr(obj, "on_click"):
                        continue
                    pos = event.pos

                    if (
                        obj.box is not None
                        and obj.visible
                        and pygame.Rect(obj.box).collidepoint(pos[0], pos[1])
                    ):
                        transformed_pos = (
                            pos[0] - obj.screen_pos[0],
                            pos[1] - obj.screen_pos[1],
                        )
                        obj.on_click(*transformed_pos)
                        event.consumed = True

    @staticmethod
    def back():
        ScreenManager.get_instance().go_back()

    @staticmethod
    def goto(screen, *args, **kwargs):
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
