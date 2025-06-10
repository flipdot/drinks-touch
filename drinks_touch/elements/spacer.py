from elements.base_elm import BaseElm


class Spacer(BaseElm):
    """
    Doesn't render anything, just takes up space.
    Use "width" and "height" to set the size of the spacer.
    """

    def __init__(self, *args, width=0, height=0, **kwargs):
        super().__init__(*args, **kwargs, width=width, height=height)

    def _render(self, *args, **kwargs):
        return None
