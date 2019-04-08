from trezor import ui
from trezor.messages import ButtonRequestType
from trezor.messages.TezosPublicKey import TezosPublicKey
from trezor.ui.text import Text
from trezor.utils import chunks

from apps.common import paths, seed
from apps.common.confirm import require_confirm
from apps.tezos import CURVE, helpers


async def get_public_key(ctx, msg, keychain):
    await paths.validate_path(
        ctx, helpers.validate_full_path, keychain, msg.address_n, CURVE
    )

    node = keychain.derive(msg.address_n, CURVE)
    pk = seed.remove_ed25519_prefix(node.public_key())
    pk_prefixed = helpers.base58_encode_check(pk, prefix=helpers.TEZOS_PUBLICKEY_PREFIX)

    if msg.show_display:
        await _show_tezos_pubkey(ctx, pk_prefixed)

    return TezosPublicKey(public_key=pk_prefixed)


async def _show_tezos_pubkey(ctx, pubkey):
    lines = chunks(pubkey, 18)
    text = Text("Confirm public key", ui.ICON_RECEIVE, icon_color=ui.GREEN)
    text.mono(*lines)
    return await require_confirm(ctx, text, code=ButtonRequestType.PublicKey)
