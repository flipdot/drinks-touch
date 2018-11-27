from .base_elm import BaseElm


class ElmList(BaseElm):
    def __init__(self, screen, **kwargs):
        self.screen = screen
        self.pos = kwargs.get('pos', (0, 0))
        self.elm_margin = kwargs.get('elm_margin', 5)
        self.max_elm_count = kwargs.get('max_elm_count', 10)
        self.elm_size = kwargs.get('elm_size', 25)

        self.__next_elm_post = self.pos[1]
        self.elements = []

    def add_elm(self, elm):
        elm.pos = (self.pos[0], self.__next_elm_post)
        self.elements.append(elm)
        self.__update_elements()

    def __update_elements(self):
        if len(self.elements) > self.max_elm_count:
            self.elements.pop(0)
            for e in self.elements:
                e.pos = (
                    self.pos[0],
                    e.pos[1] - (e.height + self.elm_margin)
                )
        else:
            last_elm = self.elements[len(self.elements) - 1:][0]
            last_elm_pos = last_elm.pos[1]
            self.__next_elm_post = last_elm_pos + last_elm.height + self.elm_margin

    def render(self):
        for e in self.elements:
            e.render()
