from elements.progress import Progress


class Screen(object):
    def __init__(self, screen):
        self.screen = screen
        self.objects = []

    def render(self, dt):
        for o in self.objects:
            if o.visible():
                if isinstance(o, Progress):
                    o.render(dt)
                else:
                    o.render()

    def events(self, events):
        for o in self.objects:
            o.events(events)
