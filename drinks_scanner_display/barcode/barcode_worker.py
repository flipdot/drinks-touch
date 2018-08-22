import datetime

class Worker:
    def __init__(self):
        pass

    def on_barcode(self, barcode):
        from screens.screen_manager import ScreenManager
        screen = ScreenManager.get_instance().get_active()
        if 'on_barcode' in dir(screen):
            screen.on_barcode(barcode)    