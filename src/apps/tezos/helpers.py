from micropython import const

from trezor.crypto import base58

from apps.common import HARDENED

TEZOS_AMOUNT_DIVISIBILITY = const(6)
TEZOS_ED25519_ADDRESS_PREFIX = "tz1"
TEZOS_ORIGINATED_ADDRESS_PREFIX = "KT1"
TEZOS_PUBLICKEY_PREFIX = "edpk"
TEZOS_SIGNATURE_PREFIX = "edsig"
TEZOS_PREFIX_BYTES = {
    # addresses
    "tz1": [6, 161, 159],
    "tz2": [6, 161, 161],
    "tz3": [6, 161, 164],
    "KT1": [2, 90, 121],
    # public keys
    "edpk": [13, 15, 37, 217],
    # signatures
    "edsig": [9, 245, 205, 134, 18],
    # operation hash
    "o": [5, 116],
}


def base58_encode_check(payload, prefix=None):
    result = payload
    if prefix is not None:
        result = bytes(TEZOS_PREFIX_BYTES[prefix]) + payload
    return base58.encode_check(result)


def base58_decode_check(enc, prefix=None):
    decoded = base58.decode_check(enc)
    if prefix is not None:
        decoded = decoded[len(TEZOS_PREFIX_BYTES[prefix]) :]
    return decoded


def validate_full_path(path: list) -> bool:
    """
    Validates derivation path to equal 44'/1729'/a',
    where `a` is an account index from 0 to 1 000 000.
    """
    if len(path) != 3:
        return False
    if path[0] != 44 | HARDENED:
        return False
    if path[1] != 1729 | HARDENED:
        return False
    if path[2] < HARDENED or path[2] > 1000000 | HARDENED:
        return False
    return True
