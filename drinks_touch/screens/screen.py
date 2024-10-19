from screens.screen_manager import ScreenManager


class Screen(object):
    def __init__(self, screen):
        self.screen = screen
        self.objects = []

    def render(self, dt):
        for o in self.objects:
            if o.visible():
                o.render(dt)

    def events(self, events):
        for o in self.objects:
            o.events(events)

    @staticmethod
    def back():
        ScreenManager.get_instance().go_back()
