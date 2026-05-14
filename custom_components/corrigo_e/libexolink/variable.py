"""
EXOline variable reference parsing and address encoding.

Variable reference string format:
  "<scope>,<ln>,<cell>,<datatype>"   e.g. "V,3,489,X" or "V,3,0x1E9,X"
  "T,<ln>"                           e.g. "T,3"  (string/text)

Scopes:
  L = Local     — 1-byte cell address (0–255)
  V = Variable  — Parameter scope; cell encoded as cell_high/cell_low (÷60 / %60)
  B = Block     — 2-byte little-endian address
  T = Text      — string variable; no cell

Data types:
  R = Real     (float32 LE)
  I = Integer  (int16 LE)
  L = Logic    (uint8, 0/1)
  X = Index    (uint8, 0–255)
  $ = String   (byte string)
"""

import struct
from dataclasses import dataclass
from typing import Union

from .exceptions import EXOError


@dataclass(frozen=True)
class VariableRef:
    """
    An EXOline variable address parsed from a reference string.

    A reference string has the form ``"<scope>,<ln>,<cell>,<datatype>"``
    where *cell* may be decimal or hex (``0x...``).  String variables use
    the shorter form ``"T,<ln>"``.

    Attributes
    ----------
    scope : str
        ``'L'`` Local, ``'V'`` Variable/Parameter, ``'B'`` Block, ``'T'`` Text.
    ln : int
        Line number — identifies the function block inside the controller.
        Typical values: 2 = setpoint/command (R/W), 3 = actual/status (R),
        43 = time channel.
    cell : int
        Cell address within the scope.  0 for Text variables.
    datatype : str
        ``'R'`` Real (float32), ``'I'`` Integer (int16), ``'L'`` Logic (bool),
        ``'X'`` Index (uint8), ``'$'`` String.
    """
    scope: str       # 'L', 'V', 'B', 'T'
    ln: int
    cell: int        # 0 for 'T' scope
    datatype: str    # 'R', 'I', 'L', 'X', '$'

    @classmethod
    def parse(cls, s: str) -> "VariableRef":
        """
        Parse a variable reference string.

        Accepts decimal or hex (0x...) cell values.
        Examples:
          "V,3,489,X"
          "V,3,0x1E9,X"
          "L,3,132,R"
          "T,3"
        """
        parts = [p.strip() for p in s.split(",")]
        scope = parts[0].upper()
        if scope == "T":
            if len(parts) < 2:
                raise EXOError(f"Invalid text reference: {s!r}")
            return cls(scope="T", ln=int(parts[1], 0), cell=0, datatype="$")
        if len(parts) < 4:
            raise EXOError(f"Invalid variable reference: {s!r}")
        return cls(
            scope=scope,
            ln=int(parts[1], 0),
            cell=int(parts[2], 0),
            datatype=parts[3].upper(),
        )

    def __str__(self) -> str:
        if self.scope == "T":
            return f"T,{self.ln}"
        return f"{self.scope},{self.ln},{self.cell},{self.datatype}"

    def address_bytes(self) -> bytes:
        """
        Encode the address fields for use in a command frame (bytes after the opcode).

        Encoding depends on scope:

        - **Local (L):** ``ln, cell`` — 2 bytes; cell is a plain 0–255 index.
        - **Variable/Parameter (V):** ``ln, cell_high, cell_low`` — 3 bytes;
          the cell number is split as ``cell_high = cell // 60`` and
          ``cell_low = cell % 60`` (inherited from the 6-bit serial EXOline
          encoding; max cell ≈ 15 299).
        - **Block (B):** ``ln, addr_low, addr_high`` — 3 bytes; 16-bit
          little-endian address.

        Returns
        -------
        bytes
            Encoded address ready to append to an opcode byte in a frame.

        Raises
        ------
        EXOError
            If the scope is unsupported or the cell value is out of range.
        """
        if self.scope == "L":
            if not 0 <= self.cell <= 255:
                raise EXOError(f"Local cell out of range: {self.cell}")
            return bytes([self.ln, self.cell])
        elif self.scope == "V":
            cell_high = self.cell // 60
            cell_low = self.cell % 60
            return bytes([self.ln, cell_high, cell_low])
        elif self.scope == "B":
            if not 0 <= self.cell <= 65535:
                raise EXOError(f"Block address out of range: {self.cell}")
            return bytes([self.ln, self.cell & 0xFF, (self.cell >> 8) & 0xFF])
        else:
            raise EXOError(f"Unsupported scope for address encoding: {self.scope!r}")


# --- Value encoding ---

def encode_value(datatype: str, value) -> bytes:
    """
    Encode a Python value to EXOline wire bytes for use in a write command.

    Parameters
    ----------
    datatype : str
        ``'R'`` float → 4-byte IEEE 754 LE; ``'I'`` int → 2-byte signed LE;
        ``'L'`` bool → 1 byte (0 or 1); ``'X'`` int → 1 byte unsigned;
        ``'$'`` str/bytes → raw bytes.
    value
        Python value compatible with *datatype*.

    Raises
    ------
    EXOError
        If the value is out of range for its type or *datatype* is unknown.
    """
    if datatype == "R":
        return struct.pack("<f", float(value))
    elif datatype == "I":
        if not -32768 <= value <= 32767:
            raise EXOError(f"Integer out of range: {value}")
        return struct.pack("<h", int(value))
    elif datatype == "L":
        return bytes([1 if value else 0])
    elif datatype == "X":
        if not 0 <= value <= 255:
            raise EXOError(f"Index out of range: {value}")
        return bytes([int(value)])
    elif datatype == "$":
        if isinstance(value, str):
            return value.encode()
        return bytes(value)
    else:
        raise EXOError(f"Unknown datatype: {datatype!r}")


def decode_value(datatype: str, data: bytes) -> Union[float, int, bool, bytes]:
    """
    Decode raw EXOline response bytes into a Python value.

    Parameters
    ----------
    datatype : str
        Expected type code (``'R'``, ``'I'``, ``'L'``, ``'X'``, or ``'$'``).
    data : bytes
        Payload bytes from a parsed response frame (checksum already removed).

    Returns
    -------
    float
        For ``'R'`` (IEEE 754 single, LE).
    int
        For ``'I'`` (signed 16-bit) or ``'X'`` (unsigned 8-bit).
    bool
        For ``'L'``; any non-zero byte is ``True``.
    bytes
        For ``'$'``.

    Raises
    ------
    EXOError
        If *data* is too short for the requested type.
    """
    if datatype == "R":
        if len(data) < 4:
            raise EXOError(f"Too few bytes for Real: {data.hex()}")
        return struct.unpack("<f", data[:4])[0]
    elif datatype == "I":
        if len(data) < 2:
            raise EXOError(f"Too few bytes for Integer: {data.hex()}")
        return struct.unpack("<h", data[:2])[0]
    elif datatype == "L":
        if len(data) < 1:
            raise EXOError(f"Too few bytes for Logic: {data.hex()}")
        return data[0] != 0
    elif datatype == "X":
        if len(data) < 1:
            raise EXOError(f"Too few bytes for Index: {data.hex()}")
        return data[0]
    elif datatype == "$":
        return data
    else:
        raise EXOError(f"Unknown datatype: {datatype!r}")


def expected_response_size(datatype: str) -> int:
    """
    Return the expected payload byte count for a read response of *datatype*.

    Returns ``-1`` for ``'$'`` (String) because the length is variable and
    cannot be used to distinguish a value from an error code.
    """
    return {"R": 4, "I": 2, "L": 1, "X": 1, "$": -1}[datatype]
