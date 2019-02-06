import math
import utime
from micropython import const
from trezorui import Display

from trezor import io, loop, res, utils, workflow

display = Display()

# in debug mode, display an indicator in top right corner
if __debug__:

    def debug_display_refresh():
        display.bar(Display.WIDTH - 8, 0, 8, 8, 0xF800)
        display.refresh()

    loop.after_step_hook = debug_display_refresh

# in both debug and production, emulator needs to draw the screen explicitly
elif utils.EMULATOR:
    loop.after_step_hook = display.refresh

# re-export constants from modtrezorui
NORMAL = Display.FONT_NORMAL
BOLD = Display.FONT_BOLD
MONO = Display.FONT_MONO
MONO_BOLD = Display.FONT_MONO_BOLD
SIZE = Display.FONT_SIZE
WIDTH = Display.WIDTH
HEIGHT = Display.HEIGHT


def lerpi(a: int, b: int, t: float) -> int:
    return int(a + t * (b - a))


def rgb(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3)


def blend(ca: int, cb: int, t: float) -> int:
    return rgb(
        lerpi((ca >> 8) & 0xF8, (cb >> 8) & 0xF8, t),
        lerpi((ca >> 3) & 0xFC, (cb >> 3) & 0xFC, t),
        lerpi((ca << 3) & 0xF8, (cb << 3) & 0xF8, t),
    )


# import style definitions
from trezor.ui.style import *  # isort:skip


def contains(area: tuple, pos: tuple) -> bool:
    x, y = pos
    ax, ay, aw, ah = area
    return ax <= x <= ax + aw and ay <= y <= ay + ah


def rotate(pos: tuple) -> tuple:
    r = display.orientation()
    if r == 0:
        return pos
    x, y = pos
    if r == 90:
        return (y, WIDTH - x)
    if r == 180:
        return (WIDTH - x, HEIGHT - y)
    if r == 270:
        return (HEIGHT - y, x)


def pulse(delay: int):
    while True:
        # normalize sin from interval -1:1 to 0:1
        yield 0.5 + 0.5 * math.sin(utime.ticks_us() / delay)


async def alert(count: int = 3):
    short_sleep = loop.sleep(20000)
    long_sleep = loop.sleep(80000)
    current = display.backlight()
    for i in range(count * 2):
        if i % 2 == 0:
            display.backlight(BACKLIGHT_MAX)
            yield short_sleep
        else:
            display.backlight(BACKLIGHT_NORMAL)
            yield long_sleep
    display.backlight(current)


async def click() -> tuple:
    touch = loop.wait(io.TOUCH)
    while True:
        ev, *pos = yield touch
        if ev == io.TOUCH_START:
            break
    while True:
        ev, *pos = yield touch
        if ev == io.TOUCH_END:
            break
    return pos


async def backlight_slide(val: int, delay: int = 35000, step: int = 20):
    sleep = loop.sleep(delay)
    current = display.backlight()
    for i in range(current, val, -step if current > val else step):
        display.backlight(i)
        yield sleep


def backlight_slide_sync(val: int, delay: int = 35000, step: int = 20):
    current = display.backlight()
    for i in range(current, val, -step if current > val else step):
        display.backlight(i)
        utime.sleep_us(delay)


def layout(f):
    async def inner(*args, **kwargs):
        await backlight_slide(BACKLIGHT_DIM)
        slide = backlight_slide(BACKLIGHT_NORMAL)
        try:
            layout = f(*args, **kwargs)
            workflow.onlayoutstart(layout)
            loop.schedule(slide)
            display.clear()
            return await layout
        finally:
            loop.close(slide)
            workflow.onlayoutclose(layout)

    return inner


def layout_no_slide(f):
    async def inner(*args, **kwargs):
        try:
            layout = f(*args, **kwargs)
            workflow.onlayoutstart(layout)
            return await layout
        finally:
            workflow.onlayoutclose(layout)

    return inner


def header(
    title: str, icon: bytes = ICON_DEFAULT, fg: int = FG, bg: int = BG, ifg: int = GREEN
):
    if icon is not None:
        display.icon(14, 15, res.load(icon), ifg, bg)
    display.text(44, 35, title, BOLD, fg, bg)


VIEWX = const(6)
VIEWY = const(9)


def grid(
    i: int,
    n_x: int = 3,
    n_y: int = 5,
    start_x: int = VIEWX,
    start_y: int = VIEWY,
    end_x: int = (WIDTH - VIEWX),
    end_y: int = (HEIGHT - VIEWY),
    cells_x: int = 1,
    cells_y: int = 1,
    spacing: int = 0,
):
    w = (end_x - start_x) // n_x
    h = (end_y - start_y) // n_y
    x = (i % n_x) * w
    y = (i // n_x) * h
    return (x + start_x, y + start_y, (w - spacing) * cells_x, (h - spacing) * cells_y)


class Widget:
    tainted = True

    def taint(self):
        self.tainted = True

    def render(self):
        pass

    def touch(self, event, pos):
        pass

    def __iter__(self):
        touch = loop.wait(io.TOUCH)
        result = None
        while result is None:
            self.render()
            event, *pos = yield touch
            result = self.touch(event, pos)
        return result


# widget-like retained UI, without explicit loop


RENDER = const(-1234)


class Control:
    def dispatch(self, event, x, y):
        if event == RENDER:
            self.render()
        elif event == TOUCH_START:
            self.touch_start(x, y)
        elif event == TOUCH_MOVE:
            self.touch_move(x, y)
        elif event == TOUCH_END:
            self.touch_end(x, y)

    def render(self):
        pass

    def touch_start(self, x, y):
        pass

    def touch_move(self, x, y):
        pass

    def touch_end(self, x, y):
        pass


# button states
INITIAL = const(0)
PRESSED = const(1)
RELEASED = const(2)
# button events
CLICK = const(1)


class Button(Control):
    def __init__(self, area: tuple, content: str):
        self.area = area
        self.content = content
        self.state = INITIAL
        self.dirty = True

    def render(self):
        if self.dirty:
            ax, ay, aw, ah = self.area
            self.render_background(ax, ay, aw, ah)
            self.render_content(ax, ay, aw, ah)
            self.dirty = False

    def render_background(self, ax, ay, aw, ah):
        pass

    def render_content(self, ax, ay, aw, ah):
        pass

    def touch_start(self, event, x, y):
        if contains(self.area, x, y):
            self.press_start(x, y)
            self.state = PRESSED
            self.dirty = True

    def touch_move(self, event, x, y):
        if contains(self.area, x, y):
            if self.state == RELEASED:
                self.press_start()
                self.state = PRESSED
                self.dirty = True
        else:
            if state == PRESSED:
                self.press_end()
                self.state = RELEASED
                self.dirty = True

    def touch_end(self, event, x, y):
        if contains(self.area, x, y):
            if self.state == PRESSED:
                self.press_end()
                self.click(x, y)
        if self.state != INITIAL:
            self.state = INITIAL
            self.dirty = True

    def press_start(self):
        pass

    def press_end(self):
        pass

    def click(self, x, y):
        pass


class Loader(Control):
    def __init__(self, target_ms=1000):
        self.target_ms = target_ms
        self.start_ms = None
        self.stop_ms = None

    def start(self):
        self.start_ms = utime.ticks_ms()
        self.stop_ms = None

    def stop(self):
        self.stop_ms = utime.ticks_ms()

    def time_since_start(self):
        if self.start_ms is None:
            return 0
        return utime.ticks_ms() - self.start_ms

    def render(self):
        target = self.target_ms
        start = self.start_ms
        stop = self.stop_ms
        now = utime.ticks_ms()
        if stop is None:
            r = min(now - start, target)
        else:
            r = max(stop - start + (stop - now) * _SHRINK_BY, 0)
            if r == 0:
                self.start_ms = None
                self.stop_ms = None
                return
        # render


class Confirm(Control):
    def __init__(self, content):
        self.confirm = Button(ui.grid(9, n_x=2), "Confirm")
        self.cancel = Button(ui.grid(8, n_x=2), "Cancel")

    def dispatch(self, event, x, y):
        self.confirm.dispatch(event, x, y)
        self.cancel.dispatch(event, x, y)


class HoldToConfirm(Control):
    def __init__(self, content):
        self.button = Button(ui.grid(4, n_x=1), "Hold To Confirm")
        self.button.press_start = self.press_start
        self.button.press_end = self.press_end
        self.loader = Loader()

    def press_start(self, x, y):
        self.loader.start()

    def press_end(self, x, y):
        self.loader.stop()

    def dispatch(self, event, x, y):
        pass
