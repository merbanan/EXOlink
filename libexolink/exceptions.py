class EXOError(Exception):
    """Base class for EXOline errors."""


class EXOFrameError(EXOError):
    """Malformed frame (bad start/end marker)."""


class EXOChecksumError(EXOError):
    """XOR checksum mismatch."""


class EXONakError(EXOError):
    """NAK response (0x15) — variable not found or access denied."""


class EXOProtocolError(EXOError):
    """Unexpected response from controller."""

    def __init__(self, code: int):
        self.code = code
        messages = {
            0x40: "Framing error (bad SOM/EOM)",
            0x41: "Checksum mismatch",
            0x42: "Empty / zero-length response",
            0x47: "Logic value error (must be 0 or 1)",
            0x48: "Index value out of range (must be 0–255)",
            0x49: "Integer value out of range (must be −32768 to 32767)",
            0x50: "Real value parse error",
            0x51: "String value error",
            0x59: "Connection error",
        }
        msg = messages.get(code, f"Unknown error code 0x{code:02X}")
        super().__init__(msg)


class EXOConnectionError(EXOError):
    """TCP connection or timeout error."""
