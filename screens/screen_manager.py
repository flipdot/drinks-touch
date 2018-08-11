class ScreenManager(object):
    instance = None

    def __init__(self, screen):
        self.screen = screen
        self.current_screen = None
        self.reset_history()
        self.set_default()
        self.screen_history = None

    def set_default(self):
        from screens.wait_scan import WaitScanScreen
        self.reset_history()
        self.set_active(WaitScanScreen(self.screen))

    def set_active(self, screen):
        self.screen_history.append(screen)
        self.current_screen = screen

    def get_active(self):
        return self.current_screen

    def go_back(self):
        self.screen_history.pop()  # remove yourself
        last = self.screen_history.pop()
        return self.set_active(last)

    def reset_history(self):
        self.screen_history = []  # reset history

    @staticmethod
    def get_instance():
        return ScreenManager.instance

    @staticmethod
    def set_instance(instance):
        ScreenManager.instance = instance
