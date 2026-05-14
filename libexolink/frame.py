"""
EXOline frame encoding and decoding.

Frame structure (request):
  [ SOM=0x3C | pla | ela | opcode | params... | XOR | EOM=0x3E ]

Frame structure (response):
  [ SOA=0x3D | payload... | XOR | EOM=0x3E ]

Special bytes (0x1B, 0x3C, 0x3D, 0x3E) are escaped as:
  0x1B  (~byte & 0xFF)
"""

from .exceptions import EXOChecksumError, EXOFrameError

SOM = 0x3C
SOA = 0x3D
EOM = 0x3E
ESC = 0x1B

_SPECIAL = frozenset([SOM, SOA, EOM, ESC])


def escape(data: bytes) -> bytes:
    """Escape special bytes in a payload or checksum sequence."""
    out = bytearray()
    for b in data:
        if b in _SPECIAL:
            out.append(ESC)
            out.append(~b & 0xFF)
        else:
            out.append(b)
    return bytes(out)


def unescape(data: bytes) -> bytes:
    """Reverse escape encoding."""
    out = bytearray()
    i = 0
    while i < len(data):
        if data[i] == ESC:
            i += 1
            out.append(~data[i] & 0xFF)
        else:
            out.append(data[i])
        i += 1
    return bytes(out)


def xor_checksum(data: bytes) -> int:
    """Return the XOR of all bytes in *data*."""
    cs = 0
    for b in data:
        cs ^= b
    return cs


def build_frame(pla: int, ela: int, opcode: int, params: bytes = b"") -> bytes:
    """
    Build a complete EXOline request frame ready to send over TCP.

    Constructs ``[ SOM | pla | ela | opcode | params | XOR | EOM ]``,
    applies escape encoding to everything between SOM and EOM (inclusive
    of the XOR byte), and returns the resulting wire bytes.

    Parameters
    ----------
    pla : int
        Physical Layer Address (0x00–0xFF). Use 0xFF for direct TCP.
    ela : int
        End Layer Address / controller node number (default 0x1E = 30).
    opcode : int
        Command opcode (see ``opcodes`` module).
    params : bytes
        Opcode-specific parameter bytes (address fields, value bytes, etc.).

    Returns
    -------
    bytes
        Complete wire frame starting with SOM (0x3C) and ending with EOM (0x3E).
    """
    payload = bytes([pla, ela, opcode]) + params
    cs = xor_checksum(payload)
    return bytes([SOM]) + escape(payload + bytes([cs])) + bytes([EOM])


def parse_response(data: bytes) -> bytes:
    """
    Parse a raw EXOline response frame received from the controller.

    Expects ``[ SOA=0x3D | escaped payload | escaped XOR | EOM=0x3E ]``.
    Strips SOA and EOM, unescapes the body, verifies the XOR checksum, and
    returns the payload bytes with the checksum byte removed.

    For a direct read response the returned bytes are the raw value
    (4 bytes for Real, 2 for Integer, 1 for Logic/Index).  For a MULCMD
    response the first two bytes are a header; the caller is responsible
    for skipping them.

    Parameters
    ----------
    data : bytes
        Raw bytes as received from the socket, including SOA and EOM.

    Returns
    -------
    bytes
        Unescaped payload bytes, checksum byte excluded.

    Raises
    ------
    EXOFrameError
        If the frame does not start with SOA or end with EOM.
    EXOChecksumError
        If the computed XOR of the payload does not match the received checksum.
    """
    if len(data) < 3:
        raise EXOFrameError(f"Response too short: {data.hex()}")
    if data[0] != SOA:
        raise EXOFrameError(f"Expected SOA (0x3D), got 0x{data[0]:02X}")
    if data[-1] != EOM:
        raise EXOFrameError(f"Expected EOM (0x3E), got 0x{data[-1]:02X}")

    inner = unescape(data[1:-1])

    if len(inner) < 1:
        raise EXOFrameError("Empty response payload")

    payload = inner[:-1]
    cs = inner[-1]

    if xor_checksum(payload) != cs:
        raise EXOChecksumError(
            f"XOR mismatch: computed 0x{xor_checksum(payload):02X}, got 0x{cs:02X}"
        )

    return payload
