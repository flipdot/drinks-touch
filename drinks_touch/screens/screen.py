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
