from threading import Timer


class Debouncer:
    def __init__(self, delay: float):
        self.delay = delay
        self.timer = None

    def debounce(self, func):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(self.delay, func)
        self.timer.start()
