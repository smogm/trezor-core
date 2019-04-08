from trezor.messages.StellarAddress import StellarAddress
from trezor.messages.StellarGetAddress import StellarGetAddress

from apps.common import paths, seed
from apps.common.layout import address_n_to_str, show_address, show_qr
from apps.stellar import CURVE, helpers


async def get_address(ctx, msg: StellarGetAddress, keychain):
    await paths.validate_path(
        ctx, helpers.validate_full_path, keychain, msg.address_n, CURVE
    )

    node = keychain.derive(msg.address_n, CURVE)
    pubkey = seed.remove_ed25519_prefix(node.public_key())
    address = helpers.address_from_public_key(pubkey)

    if msg.show_display:
        desc = address_n_to_str(msg.address_n)
        while True:
            if await show_address(ctx, address, desc=desc):
                break
            if await show_qr(ctx, address.upper(), desc=desc):
                break

    return StellarAddress(address=address)
