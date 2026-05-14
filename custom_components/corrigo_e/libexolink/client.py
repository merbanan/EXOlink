"""
EXOlink TCP client.

Usage:
    from libexolink import EXOlink, VariableRef

    with EXOlink("192.168.1.100") as ctrl:
        temp = ctrl.read("V,3,0x084,R")   # outdoor temperature
        mode = ctrl.read("V,3,0x1E9,X")   # ventilation mode
        ctrl.write("V,2,0x210,R", 22.0)   # set supply setpoint
        ctrl.poll()
"""

import socket
import struct
from typing import Union

from .exceptions import EXOConnectionError, EXOError, EXONakError, EXOProtocolError
from .frame import build_frame, parse_response
from .opcodes import POLL
from .opcodes import READ_OPCODES, WRITE_OPCODES
from .variable import (
    VariableRef,
    decode_value,
    encode_value,
    expected_response_size,
)

DEFAULT_PORT = 26486
DEFAULT_PLA = 0xFF
DEFAULT_ELA = 0x1E
DEFAULT_TIMEOUT = 3.0

_ERROR_CODES = frozenset([0x15, 0x40, 0x41, 0x42, 0x47, 0x48, 0x49, 0x50, 0x51, 0x59])


class EXOlink:
    """
    Synchronous EXOline-TCP client for Regin Corrigo controllers.

    Parameters
    ----------
    host : str
        Controller IP address or hostname.
    port : int
        TCP port (default 26486).
    pla : int
        Physical Layer Address (default 0xFF).
    ela : int
        End Layer Address / controller address (default 30 = 0x1E).
    timeout : float
        Socket read timeout in seconds (default 3.0).
    """

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        pla: int = DEFAULT_PLA,
        ela: int = DEFAULT_ELA,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.host = host
        self.port = port
        self.pla = pla
        self.ela = ela
        self.timeout = timeout
        self._sock: socket.socket | None = None

    # --- Connection management ---

    def connect(self) -> None:
        """
        Open the TCP connection to the controller.

        Raises
        ------
        EXOConnectionError
            If the TCP connection cannot be established.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            self._sock = sock
        except OSError as e:
            raise EXOConnectionError(f"Cannot connect to {self.host}:{self.port}: {e}") from e

    def close(self) -> None:
        """Close the TCP connection."""
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def __enter__(self) -> "EXOlink":
        """Connect and return ``self`` for use as a context manager."""
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        """Close the connection on context manager exit (suppresses no exceptions)."""
        self.close()

    # --- Public API ---

    def poll(self) -> None:
        """
        Send a POLL (0x98) keep-alive and verify the controller ACKs.

        POLL carries no parameters.  A successful response is an empty ACK
        frame (zero-length payload).  Call this periodically to keep the
        connection alive and detect stale sockets early.

        Raises
        ------
        EXOConnectionError
            If the socket is not connected or the controller does not respond.
        EXOProtocolError
            If the controller returns a non-empty payload instead of an ACK.
        """
        frame = build_frame(self.pla, self.ela, POLL)
        payload = self._send_recv(frame)
        # Empty ACK: payload should be empty (XOR = 0x00, already stripped)
        if len(payload) != 0:
            raise EXOProtocolError(payload[0] if payload else 0)

    def read(self, ref: Union[VariableRef, str]) -> Union[float, int, bool, bytes]:
        """
        Read a variable from the controller.

        Selects the correct read opcode based on the variable's scope and
        data type, builds and sends the frame, then decodes the response.

        Parameters
        ----------
        ref : VariableRef or str
            Variable reference, e.g. ``"V,3,0x1E9,X"`` or a parsed
            :class:`VariableRef`.  Cell values may be decimal or hex.

        Returns
        -------
        float
            For Real (R) variables.
        int
            For Integer (I) and Index (X) variables.
        bool
            For Logic (L) variables.
        bytes
            For String ($) variables.

        Raises
        ------
        EXONakError
            If the controller returns NAK (0x15) — variable not found or
            access denied.
        EXOProtocolError
            If the controller returns a recognised error code other than NAK.
        EXOError
            If the scope/type combination has no matching opcode, or the
            response length is unexpected.
        EXOConnectionError
            On socket errors.
        """
        if isinstance(ref, str):
            ref = VariableRef.parse(ref)

        if ref.datatype == "$":
            return self._read_string(ref)

        opcode = READ_OPCODES.get((ref.scope, ref.datatype))
        if opcode is None:
            raise EXOError(f"No read opcode for scope={ref.scope!r} type={ref.datatype!r}")

        frame = build_frame(self.pla, self.ela, opcode, ref.address_bytes())
        payload = self._send_recv(frame)
        self._check_error(payload, ref.datatype)
        return decode_value(ref.datatype, payload)

    def write(self, ref: Union[VariableRef, str], value) -> None:
        """
        Write a value to a variable on the controller.

        Encodes *value* according to the variable's data type, builds and
        sends the write frame, then verifies the ACK response.

        Parameters
        ----------
        ref : VariableRef or str
            Variable reference, e.g. ``"V,2,0x210,R"`` or a parsed
            :class:`VariableRef`.
        value
            Value compatible with the variable's data type: ``float`` for R,
            ``int`` for I/X, ``bool`` for L, ``str`` or ``bytes`` for ``$``.

        Raises
        ------
        EXONakError
            If the controller returns NAK (0x15).
        EXOProtocolError
            If the controller returns a recognised error code (e.g. 0x47 for
            an out-of-range Logic value, 0x48 for Index, 0x49 for Integer).
        EXOError
            If *value* is out of range, the scope/type has no write opcode,
            or the response is malformed.
        EXOConnectionError
            On socket errors.
        """
        if isinstance(ref, str):
            ref = VariableRef.parse(ref)

        if ref.datatype == "$":
            self._write_string(ref, value)
            return

        opcode = WRITE_OPCODES.get((ref.scope, ref.datatype))
        if opcode is None:
            raise EXOError(f"No write opcode for scope={ref.scope!r} type={ref.datatype!r}")

        params = ref.address_bytes() + encode_value(ref.datatype, value)
        frame = build_frame(self.pla, self.ela, opcode, params)
        payload = self._send_recv(frame)
        # Success ACK has empty payload; any content is an error
        if payload:
            self._check_error(payload, ref.datatype)

    # --- Internal ---

    def _send_recv(self, frame: bytes) -> bytes:
        """Send *frame* over the socket and return the parsed response payload."""
        if self._sock is None:
            raise EXOConnectionError("Not connected")
        try:
            self._sock.sendall(frame)
            raw = self._recv_frame()
        except OSError as e:
            raise EXOConnectionError(f"Socket error: {e}") from e
        return parse_response(raw)

    def _recv_frame(self) -> bytes:
        """
        Read one complete response frame from the socket.

        Waits for SOA (0x3D) to arrive, then accumulates bytes until an
        unescaped EOM (0x3E) is seen.  An ESC byte (0x1B) puts the reader
        into an escape state so the following byte is never mistaken for EOM,
        even if its value is 0x3E.

        Returns the raw bytes from SOA through EOM inclusive; unescaping and
        XOR verification are left to :func:`parse_response`.
        """
        from .frame import EOM, ESC, SOA

        buf = bytearray()
        escape_next = False
        started = False

        while True:
            chunk = self._sock.recv(1)
            if not chunk:
                raise EXOConnectionError("Connection closed by controller")
            b = chunk[0]

            if not started:
                if b == SOA:
                    buf.append(b)
                    started = True
                continue

            buf.append(b)

            if escape_next:
                escape_next = False
                continue

            if b == ESC:
                escape_next = True
                continue

            if b == EOM:
                return bytes(buf)

    def _check_error(self, payload: bytes, datatype: str) -> None:
        """
        Raise if *payload* looks like an error response rather than a value.

        The protocol is ambiguous for 1-byte types (Logic, Index): a
        single-byte error code and a single-byte value are indistinguishable
        by length alone.  The heuristic used here is: if the payload length
        matches the expected size for *datatype*, treat it as a valid value;
        otherwise, if it is exactly 1 byte, check whether that byte is a
        known error code (0x15 NAK, 0x40–0x59 protocol errors).
        """
        expected = expected_response_size(datatype)
        if expected == -1:
            return  # variable-length string — cannot distinguish by size
        if len(payload) == expected:
            return  # correct size, not an error
        if len(payload) == 1:
            code = payload[0]
            if code == 0x15:
                raise EXONakError("Variable not found or access denied")
            if code in _ERROR_CODES:
                raise EXOProtocolError(code)
        raise EXOError(
            f"Unexpected response length {len(payload)} for type {datatype!r}: {payload.hex()}"
        )

    def _read_string(self, ref: VariableRef) -> bytes:
        from .frame import build_frame
        from .opcodes import RSV

        frame = build_frame(self.pla, self.ela, RSV, bytes([ref.ln]))
        return self._send_recv(frame)

    def _write_string(self, ref: VariableRef, value) -> None:
        from .opcodes import SSV

        if isinstance(value, str):
            value = value.encode()
        params = bytes([ref.ln]) + bytes(value)
        frame = build_frame(self.pla, self.ela, SSV, params)
        payload = self._send_recv(frame)
        if payload:
            self._check_error(payload, "$")
