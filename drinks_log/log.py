class Log:
    def __init__(self):
        pass

    def register_handler(self, handler):
        self.handler = handler

    def log(self, msg):
        self.handler(msg)
