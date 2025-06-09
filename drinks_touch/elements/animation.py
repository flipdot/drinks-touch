from .base_elm import BaseElm

import pygame


class Animation(BaseElm):
    def __init__(
        self,
        src: str,
        n_frames: int,
        frame_duration: float = 0.1,
        size=None,
        scale_smooth=True,
        *args,
        **kwargs
    ):
        self.size = size
        self.frames = [
            pygame.image.load(src.format(i)).convert_alpha() for i in range(n_frames)
        ]
        if size:
            if scale_smooth:
                self.frames = [
                    pygame.transform.smoothscale(frame, size) for frame in self.frames
                ]
            else:
                self.frames = [
                    pygame.transform.scale(frame, size) for frame in self.frames
                ]
        self.frame_duration = frame_duration
        self.ts = 0
        super().__init__(
            *args,
            height=(self.frames[0].get_height()),
            width=(self.frames[0].get_width()),
            **kwargs
        )

    def calculate_hash(self):
        super_hash = super().calculate_hash()
        return hash(
            (
                super_hash,
                self.ts,
            )
        )

    def tick(self, dt: float):
        super().tick(dt)
        self.ts += dt

    def render(self, *args, **kwargs) -> pygame.Surface:
        return self.frames[int(self.ts / self.frame_duration) % len(self.frames)]
