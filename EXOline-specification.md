# EXOline-TCP Protocol Specification

This document describes the EXOline-TCP protocol as used to communicate with Regin Corrigo building management controllers.
EXOline-TCP is a proprietary Regin AB protocol. This documentation is unofficial.

---

## Transport Layer

- **Protocol**: TCP (IPv4)
- **Default port**: 26486
- **Model**: Synchronous request/response. Client sends one command; server responds before the next command is sent. The response payload format depends on the command sent — the client must track which command is in flight.
- **Connection**: Timeout is set to 3 seconds on reads.
- **Keep-alive**: Use the POLL command (see below) to verify the connection is alive.

---

## Special Bytes

| Name | Value | Meaning |
|------|-------|---------|
| SOM  | `0x3C` | Start Of Message (client → controller) |
| SOA  | `0x3D` | Start Of Answer (controller → client) |
| EOM  | `0x3E` | End Of Message (both directions) |
| ESC  | `0x1B` | Escape byte |

These four bytes have special meaning in the framing layer and must be escaped when they appear in payload data or the checksum.

---

## Frame Structure

### Client Request

```
[ SOM=0x3C | pla | ela | opcode | params... | XOR | EOM=0x3E ]
```

| Field    | Size     | Description |
|----------|----------|-------------|
| SOM      | 1 byte   | Always `0x3C` |
| pla      | 1 byte   | Physical Layer Address. Default `0xFF` (broadcast). |
| ela      | 1 byte   | End Layer Address. Default `0x1E` (30). |
| opcode   | 1 byte   | Command opcode (see Opcode Table) |
| params   | variable | Command-specific parameters |
| XOR      | 1 byte   | XOR checksum of all bytes from `pla` through last param byte (inclusive) |
| EOM      | 1 byte   | Always `0x3E` |

The XOR checksum does **not** include SOM or EOM.

### Controller Response

```
[ SOA=0x3D | payload... | XOR | EOM=0x3E ]
```

The response payload structure depends on the command. See the Response Format section.

---

## Escape Encoding

Any occurrence of `0x1B`, `0x3C`, `0x3D`, or `0x3E` in the payload, params, or XOR byte is replaced by:

```
0x1B  (~byte & 0xFF)
```

where `~byte` is the bitwise complement (one's complement). This applies to both client requests and server responses.

**Encoding (sender):** Before appending EOM, scan all bytes from position 1 (after SOM) through the XOR byte. For each special byte found, insert `0x1B` before it and replace the byte value with its complement.

**Decoding (receiver):** Scan the received bytes (between the start marker and EOM). On encountering `0x1B`, remove it and replace the next byte with its complement.

### Example

From `Specification.md` — a temperature reading response:

```
Wire:    3d 05 00 14 c3 ae 41 1b c2 3e
Decoded: 3d 05 00 14 c3 ae 41 3d    3e
```

The XOR checksum is `0x3D` (= SOA), which is a special byte. So on the wire it appears as `1b c2` (where `~0x3D = 0xC2`). After decoding, the payload is `[05 00 14 c3 ae 41]` with checksum `3d`.

---

## XOR Checksum

**Request:** XOR of all bytes from `pla` (index 1) through the last parameter byte (inclusive). Does not include SOM or EOM.

**Response:** XOR of all unescaped payload bytes before the checksum byte. The checksum byte is the last byte before EOM.

Verification :
```
uint8_t cs = 0;
for (int k = 0; k < newLen - 1; k++)
    cs ^= okAnswer2[k];
// cs must equal okAnswer2[newLen - 1]
```

---

## PLA / ELA Addressing

EXOline was originally a serial bus protocol. The TCP version retains the bus-addressing fields:

- **PLA** (Physical Layer Address): identifies the segment or bus. Set to `0xFF` for direct TCP connections (effectively unicast/addressed-to-all on the TCP link).
- **ELA** (End Layer Address): identifies the specific controller. Default `30` (`0x1E`).

These are always present as bytes 1 and 2 of every request frame (immediately after SOM).

---

## EXOL Data Types

| Type | Code | Size   | Range            | Encoding |
|------|------|--------|------------------|----------|
| Real | `R`  | 4 bytes | ±3.4E38         | IEEE 754 single-precision float, little-endian |
| Integer | `I` | 2 bytes | −32768 to 32767 | Signed 16-bit, little-endian |
| Index | `X` | 1 byte | 0 to 255         | Unsigned 8-bit |
| Logic | `L` | 1 byte | 0 or 1           | Unsigned 8-bit; any non-zero = true |
| String | `$` | variable | —              | Byte string; encoding is OEM code page (varies by controller locale) |

---

## Variable Scopes

Each variable lives in one of three scopes that affects addressing and the opcode used:

| Scope | Code | Address field | Max address |
|-------|------|---------------|-------------|
| Local | `L`  | 1-byte `cell` (0–255) | 255 |
| Parameter | `P` | 2-byte split: `cell_high = cell / 60`, `cell_low = cell % 60` | 15,299 |
| Block | `B`  | 2-byte address little-endian: `addr_low`, `addr_high` | 65535 |

**Parameter cell encoding:** A parameter cell number is split across two bytes because the original serial EXOline protocol had 6-bit sub-fields. To encode cell `N`: `high = N / 60`, `low = N % 60`. To decode: `N = high * 60 + low`.

---

## Opcode Table

### Read Commands

| Mnemonic | Opcode | Scope | Type | Request params (after opcode) | Response data |
|----------|--------|-------|------|-------------------------------|---------------|
| RRL | `0xAE` | Local | Real | `ln` (1 byte) + `cell` (1 byte) | 4-byte float, LE |
| RIL | `0xAD` | Local | Integer | `ln` + `cell` | 2-byte int, LE |
| RLL | `0xAB` | Local | Logic | `ln` + `cell` | 1 byte (0/1) |
| RXL | `0x2C` | Local | Index | `ln` + `cell` | 1 byte (0–255) |
| RRP | `0xB6` | Parameter | Real | `ln` + `cell_high` + `cell_low` | 4-byte float, LE |
| RIP | `0xB5` | Parameter | Integer | `ln` + `cell_high` + `cell_low` | 2-byte int, LE |
| RLP | `0xB3` | Parameter | Logic | `ln` + `cell_high` + `cell_low` | 1 byte (0/1) |
| RXP | `0x34` | Parameter | Index | `ln` + `cell_high` + `cell_low` | 1 byte (0–255) |
| RRB | `0xBF` | Block | Real | `ln` + `addr_low` + `addr_high` | 4-byte float, LE |
| RIB | `0x3E` | Block | Integer | `ln` + `addr_low` + `addr_high` | 2-byte int, LE |
| RLB | `0xBC` | Block | Logic | `ln` + `addr_low` + `addr_high` | 1 byte (0/1) |
| RXB | `0x3D` | Block | Index | `ln` + `addr_low` + `addr_high` | 1 byte (0–255) |
| RSV | `0x8A` | — | String | `ln` (1 byte) | variable-length byte string |

Note: `RIB` opcode `0x3E` = EOM, and `RXB` opcode `0x3D` = SOA. These will be escape-encoded in the request frame.

### Write Commands

| Mnemonic | Opcode | Scope | Type | Request params (after opcode) | Response |
|----------|--------|-------|------|-------------------------------|----------|
| SRL | `0x2A` | Local | Real | `ln` + `cell` + 4-byte float LE | ACK/error |
| SIL | `0x29` | Local | Integer | `ln` + `cell` + 2-byte int LE | ACK/error |
| SLL | `0xA7` | Local | Logic | `ln` + `cell` + 1 byte (0/1) | ACK/error |
| SXL | `0xA8` | Local | Index | `ln` + `cell` + 1 byte value | ACK/error |
| SRP | `0x32` | Parameter | Real | `ln` + `cell_high` + `cell_low` + 4-byte float LE | ACK/error |
| SIP | `0x31` | Parameter | Integer | `ln` + `cell_high` + `cell_low` + 2-byte int LE | ACK/error |
| SLP | `0x2F` | Parameter | Logic | `ln` + `cell_high` + `cell_low` + 1 byte | ACK/error |
| SXP | `0xB0` | Parameter | Index | `ln` + `cell_high` + `cell_low` + 1 byte | ACK/error |
| SRB | `0x3B` | Block | Real | `ln` + `addr_low` + `addr_high` + 4-byte float LE | ACK/error |
| SIB | `0xBA` | Block | Integer | `ln` + `addr_low` + `addr_high` + 2-byte int LE | ACK/error |
| SLB | `0x38` | Block | Logic | `ln` + `addr_low` + `addr_high` + 1 byte | ACK/error |
| SXB | `0xB9` | Block | Index | `ln` + `addr_low` + `addr_high` + 1 byte | ACK/error |
| SSV | `0x85` | — | String | `ln` + variable-length byte string | ACK/error |

### Special Commands

| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| POLL | `0x98` | Keep-alive / connection check. Params: none. Response: empty ACK. |
| GETV | `0x10` | Bulk read of multiple variables in one request. |
| MULCMD | `0xC8` | Multi-command wrapper. Used by the C tool to wrap a single sub-command with a length prefix. |

---

## Command Frame Construction (Request)

The total payload byte count passed to `send()` is:

| Scope | Bytes after SOM before XOR | Opcode at |
|-------|---------------------------|-----------|
| Local read | pla + ela + opcode + ln + cell = 5 bytes | [3] |
| Parameter read | pla + ela + opcode + ln + cell_high + cell_low = 6 bytes | [3] |
| Block read | pla + ela + opcode + ln + addr_low + addr_high = 6 bytes | [3] |
| Local write (R) | 5 + 4 = 9 bytes | [3] |
| Parameter write (R) | 6 + 4 = 10 bytes | [3] |
| POLL | pla + ela + opcode = 3 bytes | [3] |

---

## Response Format

### Standard Read Response

For direct read commands (RRL, RIL, RXL, etc.), after stripping SOA, unescaping, and removing the XOR checksum, the remaining bytes are the raw value:

```
Data bytes: [value_byte_0, value_byte_1, ...]
```

- **Real (float):** 4 bytes, IEEE 754, little-endian. Decode as: `(b[0] & 0xFF) | ((b[1] & 0xFF) << 8) | ((b[2] & 0xFF) << 16) | ((b[3] & 0xFF) << 24)` then reinterpret as float.
- **Integer:** 2 bytes, signed 16-bit, little-endian.
- **Logic:** 1 byte; non-zero = `true`.
- **Index:** 1 byte, unsigned 0–255.

### MULCMD Response

When using the MULCMD wrapper (as in `exolink.c`), the response has a 2-byte header before the data:

```
[ SOA | hdr_b0 | hdr_b1 | value_byte_0 ... | XOR | EOM ]
```

The C code accesses the float at `pl_off = 3` (i.e., 3 bytes after SOA = 2 header bytes before float data). The header bytes appear to encode response length and a status/opcode echo; their exact meaning is not fully documented.

Full example (from `Specification.md`, temperature reading via MULCMD):
```
Wire:     3d 05 00 14 c3 ae 41 1b c2 3e
Decoded:  3d 05 00 14 c3 ae 41 3d       3e
           ^  ^  ^  ^-----------^  ^
           SOA  |  |  float data   XOR=0x3D
               hdr0 hdr1
```
Float bytes: `14 c3 ae 41` → `0x41AEC314` → ~21.85°C

### EXOSHORT Response (enum/status)

For single-byte enumerated values read via MULCMD (e.g., ventilation mode), the value is the last data byte before the XOR checksum:

```
pl_off = ans_buf_len - 3   (C code, where ans_buf includes SOA and EOM)
```

### Write / Set Command Response

A successful write returns an empty ACK frame:
```
[ SOA | XOR=0 | EOM ]
```
(zero-length payload, XOR = 0)

---

## Error Response

An error response contains a single payload byte — the error code:

```
[ SOA | error_code | XOR | EOM ]
```

Known error codes:

| Code (hex) |  Meaning |
|------------|----------|
| `0x15` |  NAK — variable not found or access denied |
| `0x40` |  Framing error (bad SOM/EOM) |
| `0x41` |  Checksum mismatch |
| `0x42` |  Empty / zero-length response |
| `0x47` |  Logic value error (write — value not 0 or 1) |
| `0x48` |  Index value out of range (write — not 0–255) |
| `0x49` |  Integer value out of range (write — not −32768 to 32767) |
| `0x50` |  Real value parse error (write) |
| `0x51` |  String value error (write) |
| `0x59` |  Connection error (local, not from controller) |

Error code `0x15` on a read response is treated as "no data" (empty result) rather than a hard error.

---

## MULCMD Wrapper (used by exolink.c)

The C tool wraps every read command inside a MULCMD frame:

```
[ SOM | pla | ela | 0xC8 | len | opcode | params... | XOR | EOM ]
```

Where `len` = number of bytes following it in the sub-command (opcode + params). For example, an RRP sub-command (opcode + ln + cell_high + cell_low) gives `len = 4`.

This wrapper format is reflected in the `exolink.config` payload hex strings. For example:

```
ff 1e c8 04 b6 03 02 0c
^  ^  ^  ^  ^  ^  ^  ^
|  |  |  |  |  ln ch cl
|  ela  len opcode=RRP
pla
```

Where: `ln=3`, `cell = 2*60 + 12 = 132`

---

## POLL Command

Used to verify connection liveness. No parameters.

```
Request:  [ 3c | pla | ela | 0x98 | XOR | 3e ]
Response: [ 3d | XOR=0 | 3e ]   (empty ACK)
```

The code should poll every ~10 iterations of the read loop (every ~150ms). After 200 consecutive null responses (~3 seconds at 15ms/iteration), it triggers a reconnect.

---

## Encryption (Sapphire Stream Cipher)

Encryption is optional and negotiated externally (via a password provided in the web UI config). When enabled:

1. After computing the XOR checksum and before escape-encoding, encrypt bytes from position 1 (pla) through the XOR byte using the Sapphire cipher.
2. Then apply escape encoding to the ciphertext.
3. On receive: unescape first, then decrypt.

The cipher is keyed on a password string. It is a 256-card shuffle-based stream cipher (similar to RC4 in structure), with state variables `rotor`, `ratchet`, `avalanche`, `lastPlain`, `lastCipher`.

For the extended command (`sendExtendedCommand`), when encryption is on, the pla/ela/marker bytes (`0x00 0x00 0xFF`) are also individually enciphered before transmission.

---

## Extended Command Format (GETV / bulk reads)

For GETV-style bulk variable reads, the request omits the pla/ela routing and instead uses a fixed 3-byte header before the data payload:

```
[ SOM=0x3C | 0x00 | 0x00 | 0xFF | data... | EOM=0x3E ]
```

No XOR checksum is used in this format (checksum is part of the inner data protocol). The response is processed by `CheckAnswerExtendedCommand`, which strips SOA/EOM and unescapes but does not verify a separate XOR — the integrity check is embedded in the GETV data layer.

---

## Variable Reference String Format

The address variables uses comma-separated reference strings parsed by `RV()` / `SV()`:

```
<scope>, <ln>, <cell>, <type>    — for scoped variables
T, <ln>                          — for text/string variables
```

| Field | Values |
|-------|--------|
| scope | `L` (Local), `V` (parameter, called "Variable"), `B` (Block), `T` (Text/String) |
| ln | Line number (integer) — identifies the function block |
| cell | Cell number within scope |
| type | `R` (Real), `I` (Integer), `L` (Logic), `X` (Index) |

Examples: `"L,3,132,R"` → Read Real Local, ln=3, cell=132. `"V,3,489,X"` → Read Index Parameter, ln=3, cell=489.

---

## RunMode Enumeration

For EXOSHORT responses returning the ventilation unit run mode (variable class X/Index):

| Value | Meaning |
|-------|---------|
| 0 | Stopped |
| 1–4 | Starting |
| 5 | Running |
| 11 | Stopping fan |
| 12 | Fire alarm |

---
