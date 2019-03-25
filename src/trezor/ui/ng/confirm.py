from trezor import res, ui
from trezor.ui.ng.button import Button, ButtonCancel, ButtonConfirm
from trezor.ui.ng.loader import Loader


CONFIRMED = object()
CANCELLED = object()


class Confirm(ui.Layout):
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


class HoldToConfirm(ui.Layout):
    def __init__(self, content, button_content="Hold To Confirm"):
        self.content = content
        self.loader = Loader()
        self.loader.on_start = self._on_loader_start
        self.button = Button(ui.grid(4, n_x=1), button_content)
        self.button.on_press_start = self._on_press_start
        self.button.on_press_end = self._on_press_end
        self.button.on_click = self._on_click

    def _on_press_start(self):
        self.loader.start()

    def _on_press_end(self):
        self.loader.stop()

    def _on_loader_start(self):
        # Loader has either started growing, or returned to the 0-position.
        # In the first case we need to clear the content leftovers, in the latter
        # we need to render the content again.
        ui.display.clear()
        self.content.dispatch(ui.REPAINT, 0, 0)
        self.button.dispatch(ui.REPAINT, 0, 0)

    def _on_click(self):
        if self.loader.elapsed_ms() >= self.loader.target_ms:
            self.on_confirm()

    def dispatch(self, event, x, y):
        if self.loader.start_ms is not None:
            self.loader.dispatch(event, x, y)
        else:
            self.content.dispatch(event, x, y)
        self.button.dispatch(event, x, y)

    def on_confirm(self):
        raise ui.Result(CONFIRMED)
