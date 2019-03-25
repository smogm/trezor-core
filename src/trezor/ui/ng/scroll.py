from micropython import const

from trezor import loop, ui
from trezor.ui.ng.swipe import SWIPE_DOWN, SWIPE_UP, SWIPE_VERTICAL, Swipe


def render_scrollbar(pages: int, page: int):
    bbox = const(220)
    size = const(8)

    padding = 14
    if pages * padding > bbox:
        padding = bbox // pages

    x = const(220)
    y = (bbox // 2) - (pages // 2) * padding

    for i in range(0, pages):
        if i == page:
            fg = ui.FG
        else:
            fg = ui.GREY
        ui.display.bar_radius(x, y + i * padding, size, size, fg, ui.BG, 4)


class Paginated(ui.Layout):
    def __init__(self, pages, page=0):
        self.pages = pages
        self.page = page

    def dispatch(self, event, x, y):
        self.pages[self.page].dispatch(event, x, y)
        if event is ui.RENDER:
            render_scrollbar(len(self.pages), self.page)

    async def __iter__(self):
        try:
            while True:
                handle_rendering = self.handle_rendering()
                handle_input = self.handle_input()
                handle_paging = self.handle_paging()
                await loop.spawn(handle_rendering, handle_input, handle_paging)
        except ui.Result as result:
            return result.value

    async def handle_paging(self):
        if self.page == 0:
            directions = SWIPE_UP
        elif self.page == len(self.pages) - 1:
            directions = SWIPE_DOWN
        else:
            directions = SWIPE_VERTICAL

        swipe = await Swipe(directions)

        if swipe is SWIPE_UP:
            self.page += 1
        elif swipe is SWIPE_DOWN:
            self.page -= 1

        self.pages[self.page].dispatch(ui.REPAINT, 0, 0)
