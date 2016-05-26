from screens.main import MainScreen

class ScreenManager(object):
    instance = None

    def __init__(self, screen):
        self.screen = screen
        self.current_screen = None
        self.set_default()

    def set_default(self):
        self.current_screen = MainScreen(self.screen)

    def set_active(self, screen):
        self.current_screen = screen

    def get_active(self):
        return self.current_screen

    @staticmethod
    def get_instance():
        return ScreenManager.instance

    @staticmethod
    def set_instance(instance):
        ScreenManager.instance = instance
