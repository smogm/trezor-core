from micropython import const

from trezor import config, log, res, ui
from trezor.ui.swipe import Swipe, degrees

from apps.common import storage


async def homescreen():
    ui.display.backlight(ui.BACKLIGHT_NORMAL)

    try:
        from trezor.ui.ng.pin import PinDialog
        from trezor.ui.ng.scroll import Paginated
        from trezor.ui.ng.passphrase import PassphraseKeyboard
        from trezor.ui.ng.mnemonic import MnemonicKeyboard
        from trezor.ui.ng.confirm import HoldToConfirm, Confirm
        from trezor.ui.ng.text import Text

        text = Text("Header")
        text.normal("Normal")
        text.mono("Mono")
        text.bold("Bold")

        text2 = Text("Page 2")
        text2.normal("Page 2")
        text2.mono("Page 2")
        text2.bold("Page 2")

        text3 = Text("Page 3")
        text3.normal("Page 3")
        text3.mono("Page 3")
        text3.bold("Page 3")

        while True:
            ui.display.clear()
            await MnemonicKeyboard("Enter the 1st word")
            await PinDialog("Change PIN")
            await HoldToConfirm(text)
            await Paginated([text, text2, Confirm(text3)])
            await PassphraseKeyboard("Enter passphrase")

    except Exception as e:
        log.exception(__name__, e)

    # while True:
    #     await ui.backlight_slide(ui.BACKLIGHT_DIM)
    #     display_homescreen()
    #     await ui.backlight_slide(ui.BACKLIGHT_NORMAL)
    #     await swipe_to_rotate()


def display_homescreen():
    if not storage.is_initialized():
        label = "Go to trezor.io/start"
        image = None
    else:
        label = storage.get_label() or "My TREZOR"
        image = storage.get_homescreen()

    if not image:
        image = res.load("apps/homescreen/res/bg.toif")

    if storage.is_initialized() and storage.no_backup():
        ui.display.bar(0, 0, ui.WIDTH, 30, ui.RED)
        ui.display.text_center(ui.WIDTH // 2, 22, "SEEDLESS", ui.BOLD, ui.WHITE, ui.RED)
        ui.display.bar(0, 30, ui.WIDTH, ui.HEIGHT - 30, ui.BG)
    elif storage.is_initialized() and storage.unfinished_backup():
        ui.display.bar(0, 0, ui.WIDTH, 30, ui.RED)
        ui.display.text_center(
            ui.WIDTH // 2, 22, "BACKUP FAILED!", ui.BOLD, ui.WHITE, ui.RED
        )
        ui.display.bar(0, 30, ui.WIDTH, ui.HEIGHT - 30, ui.BG)
    elif storage.is_initialized() and storage.needs_backup():
        ui.display.bar(0, 0, ui.WIDTH, 30, ui.YELLOW)
        ui.display.text_center(
            ui.WIDTH // 2, 22, "NEEDS BACKUP!", ui.BOLD, ui.BLACK, ui.YELLOW
        )
        ui.display.bar(0, 30, ui.WIDTH, ui.HEIGHT - 30, ui.BG)
    elif storage.is_initialized() and not config.has_pin():
        ui.display.bar(0, 0, ui.WIDTH, 30, ui.YELLOW)
        ui.display.text_center(
            ui.WIDTH // 2, 22, "PIN NOT SET!", ui.BOLD, ui.BLACK, ui.YELLOW
        )
        ui.display.bar(0, 30, ui.WIDTH, ui.HEIGHT - 30, ui.BG)
    else:
        ui.display.bar(0, 0, ui.WIDTH, ui.HEIGHT, ui.BG)
    ui.display.avatar(48, 48 - 10, image, ui.WHITE, ui.BLACK)
    ui.display.text_center(ui.WIDTH // 2, 220, label, ui.BOLD, ui.FG, ui.BG)


async def swipe_to_rotate():
    swipe = await Swipe(absolute=True)
    ui.display.orientation(degrees(swipe))
