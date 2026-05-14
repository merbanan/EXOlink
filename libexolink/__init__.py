"""
libexolink — EXOline-TCP client library for Regin Corrigo controllers.

Implements the EXOline-TCP framing protocol (escape encoding, XOR checksum,
PLA/ELA addressing) and exposes a simple read/write API for all variable
scopes and data types defined in the protocol.

See ``EXOline-specification.md`` for the full protocol reference and
``variable-specification.md`` for Corrigo E variable addresses.

Quick start
-----------
::

    from libexolink import EXOlink, VariableRef

    with EXOlink("192.168.1.100") as ctrl:
        temp = ctrl.read("V,3,0x084,R")    # outdoor temperature (float)
        mode = ctrl.read("V,3,0x1E9,X")    # ventilation mode (int 0–14)
        ctrl.write("V,2,0x210,R", 22.0)    # write supply setpoint
        ctrl.poll()                         # keep-alive check

Variable references
-------------------
``"<scope>,<ln>,<cell>,<datatype>"`` — cell may be decimal or hex.

- Scope ``V`` (Parameter): most setpoints and status variables.
- Scope ``L`` (Local): single-byte addressed variables.
- Scope ``B`` (Block): 16-bit addressed variables.
- ln=2 → setpoint/command (R/W); ln=3 → actual/status (R).

Exceptions
----------
All errors are subclasses of :class:`EXOError`:

- :class:`EXOConnectionError` — TCP socket / timeout failure.
- :class:`EXOFrameError` — malformed frame (bad SOA/EOM marker).
- :class:`EXOChecksumError` — XOR mismatch in received frame.
- :class:`EXONakError` — controller returned NAK (variable not found).
- :class:`EXOProtocolError` — controller returned a protocol error code.
"""

from .client import EXOlink
from .exceptions import (
    EXOChecksumError,
    EXOConnectionError,
    EXOError,
    EXOFrameError,
    EXONakError,
    EXOProtocolError,
)
from .variable import VariableRef, decode_value, encode_value

__all__ = [
    "EXOlink",
    "VariableRef",
    "encode_value",
    "decode_value",
    "EXOError",
    "EXOFrameError",
    "EXOChecksumError",
    "EXONakError",
    "EXOProtocolError",
    "EXOConnectionError",
]
