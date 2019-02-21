from trezor import res, ui
from trezor.ui.ng.button import Button, ButtonCancel, ButtonConfirm
from trezor.ui.ng.loader import Loader


CONFIRMED = object()
CANCELLED = object()


class Confirm(ui.Control):
    def __init__(self, content):
        self.content = content

        icon_confirm = res.load(ui.ICON_CONFIRM)
        self.confirm = Button(ui.grid(9, n_x=2), icon_confirm, ButtonConfirm)
        self.confirm.on_click = self.on_confirm

        icon_cancel = res.load(ui.ICON_CANCEL)
        self.cancel = Button(ui.grid(8, n_x=2), icon_cancel, ButtonCancel)
        self.cancel.on_click = self.on_cancel

    def dispatch(self, event, x, y):
        self.content.dispatch(event, x, y)
        self.confirm.dispatch(event, x, y)
        self.cancel.dispatch(event, x, y)

    def on_confirm(self):
        raise ui.Result(CONFIRMED)

    def on_cancel(self):
        raise ui.Result(CANCELLED)


class HoldToConfirm(ui.Control):
    def __init__(self, content):
        self.content = content
        self.loader = Loader()
        self.button = Button(ui.grid(4, n_x=1), "Hold To Confirm")
        self.button.on_press_start = self._on_press_start
        self.button.on_press_end = self._on_press_end
        self.button.on_click = self._on_click

    def _on_press_start(self):
        self.loader.start()

    def _on_press_end(self):
        self.loader.stop()

    def _on_click(self):
        elapsed = self.loader.ms_since_start()
        if elapsed >= self.loader.target_ms:
            self.on_confirm()

    def dispatch(self, event, x, y):
        if self.loader.start_ms is not None:
            self.loader.dispatch(event, x, y)
        else:
            self.content.dispatch(event, x, y)
        self.button.dispatch(event, x, y)

    def on_confirm(self):
        raise ui.Result(CONFIRMED)
