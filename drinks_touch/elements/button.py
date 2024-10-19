from env import monospace
from icons.base import BaseIcon
from .base_elm import BaseElm

import contextlib

with contextlib.redirect_stdout(None):
    import pygame


class Button(BaseElm):
    def __init__(
        self,
        screen,
        font=monospace,
        size=30,
        text="<Label>",
        color=(246, 198, 0),
        click_func=None,
        click_func_param=None,
        click_param=None,
        padding=10,
        force_width=None,
        force_height=None,
        icon: BaseIcon = None,
        pos=(0, 0),
    ):
        self.font = font
        self.size = size
        self.text = text
        self.color = color
        self.clicked = click_func or self.__clicked
        self.clicked_param = click_func_param
        self.click_param = click_param
        self.padding = padding
        self.force_width = force_width
        self.force_height = force_height
        self.icon = icon

        self.box = None
        self.clicking = False

        super(Button, self).__init__(screen, pos, self.size, -1)

        self.__load_font()

    def __load_font(self):
        self.font = pygame.font.SysFont(self.font, self.size)

    @staticmethod
    def __clicked():
        print("Clicked on button without handler")

    def pre_click(self):
        self.clicking = True

    def post_click(self):
        self.clicking = False

    def render(self, *args, **kwargs):
        if self.clicking:
            self.screen.fill(tuple(c * 0.7 for c in self.color), self.box)

        top = self.pos[0] - self.padding
        left = self.pos[1] - self.padding
        width = self.padding * 2
        height = self.padding * 2

        if self.icon:
            icon_element = self.icon.render()
            width += icon_element.get_width()
            height += icon_element.get_height()
            self.screen.blit(icon_element, self.pos)
            text_pos = (
                self.pos[0] + icon_element.get_width() + self.padding,
                self.pos[1],
            )
        else:
            text_pos = self.pos
            icon_element = None

        if self.text:
            text_element = self.font.render(self.text, 1, self.color)
            width += text_element.get_width()
            if icon_element:
                width += 10
                if icon_element.get_height() > text_element.get_height():
                    height = icon_element.get_height() + self.padding * 2
            else:
                height = text_element.get_height() + self.padding * 2
            self.screen.blit(text_element, text_pos)

            if self.force_width is not None:
                width = self.force_width
                top = self.pos[0] + text_element.get_width() / 2 - width / 2
            if self.force_height is not None:
                height = self.force_height
                left = self.pos[1] + text_element.get_height() / 2 - height / 2

        self.box = (top, left, width, height)

        pygame.draw.rect(self.screen, self.color, self.box, 1)

    def events(self, events):
        for event in events:
            if "consumed" in event.dict and event.consumed:
                continue

            if event.type == pygame.MOUSEBUTTONUP:
                pos = event.pos

                if (
                    self.box is not None
                    and self.visible()
                    and pygame.Rect(self.box).collidepoint(pos[0], pos[1])
                ):
                    self.pre_click()
                    try:
                        if self.click_param:
                            self.clicked_param(self.click_param)
                        else:
                            self.clicked()
                    finally:
                        self.post_click()
                    event.consumed = True
