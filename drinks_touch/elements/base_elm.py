class BaseElm(object):
    def __init__(self, screen, pos=None, height=None, width=None):
        self.screen = screen
        self.pos = pos
        self._height = height
        self._width = width
        self.is_visible = True

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    def events(self, events):
        pass

    def visible(self):
        return self.is_visible

    def render(self, *args, **kwargs):
        pass
