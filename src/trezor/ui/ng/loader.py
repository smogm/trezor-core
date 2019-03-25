import utime

from trezor import ui
from trezor.ui import display


class Loader(ui.Control):
    def __init__(self, target_ms=1000):
        self.target_ms = target_ms
        self.start_ms = None
        self.stop_ms = None

    def start(self):
        self.start_ms = utime.ticks_ms()
        self.stop_ms = None
        self.on_start()

    def stop(self):
        self.stop_ms = utime.ticks_ms()

    def elapsed_ms(self):
        if self.start_ms is None:
            return 0
        return utime.ticks_ms() - self.start_ms

    def on_render(self):
        target = self.target_ms
        start = self.start_ms
        stop = self.stop_ms
        now = utime.ticks_ms()
        if stop is None:
            r = min(now - start, target)
        else:
            r = max(stop - start + (stop - now) * 2, 0)
        display.loader(r, -24, ui.FG, ui.BG)
        if r == 0:
            self.start_ms = None
            self.stop_ms = None
            self.on_start()

    def on_start(self):
        pass
