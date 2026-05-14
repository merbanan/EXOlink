# EXOlink

Tools and libraries for communicating with Regin Corrigo E ventilation controllers over the EXOline-TCP protocol.

> This project is not affiliated with Regin AB. Use at your own risk.

---

## Contents

- **`libexolink/`** — Python library for EXOline-TCP communication
- **`corrigo.py`** — Command-line tool for reading and writing Corrigo E variables
- **`custom_components/corrigo_e/`** — Home Assistant integration (HACS)

---

## libexolink

A pure-Python library that implements EXOline-TCP framing, addressing, and variable encoding. No external dependencies.

### Installation

Copy the `libexolink/` directory into your project, or install directly from this repository:

```bash
pip install git+https://github.com/merbanan/EXOlink.git
```

### Usage

```python
from libexolink import EXOlink

with EXOlink("192.168.1.100") as ctrl:
    # Read the current ventilation mode (integer, 0–14)
    mode = ctrl.read("V,3,0x1E9,X")
    print(mode)  # e.g. 5

    # Read outdoor temperature (float, °C)
    temp = ctrl.read("V,3,0x084,R")
    print(f"{temp:.1f} °C")  # e.g. 7.3 °C

    # Read supply air temperature
    supply = ctrl.read("V,3,0x087,R")
    print(f"{supply:.1f} °C")

    # Write a new supply air setpoint
    ctrl.write("V,2,0x210,R", 22.0)

    # Write ventilation mode: 3 = Auto
    ctrl.write("V,2,0x321,X", 3)
```

Variable references have the form `"<scope>,<ln>,<cell>,<datatype>"`:

| Field | Meaning |
|---|---|
| scope | `V` = parameter, `L` = local, `B` = block |
| ln | Line number — `2` = setpoint (R/W), `3` = actual/status (R) |
| cell | Address (decimal or hex, e.g. `0x1E9`) |
| datatype | `R` = float, `I` = int16, `L` = bool, `X` = enum (uint8) |

See `CorrigoEVentilation.variables` for the full list of named variables and their references.

### Exceptions

All errors are subclasses of `EXOError`:

| Exception | Meaning |
|---|---|
| `EXOConnectionError` | TCP socket or timeout failure |
| `EXONakError` | Controller returned NAK — variable not found or access denied |
| `EXOProtocolError` | Controller returned a protocol error code |
| `EXOFrameError` | Malformed response frame |
| `EXOChecksumError` | XOR checksum mismatch |

---

## corrigo.py — Command-line tool

```
Usage:
  corrigo.py HOST read  VAR [VAR ...]    read by name or ref
  corrigo.py HOST write VAR VALUE        write by name or ref
  corrigo.py HOST list  [FILTER]         list known variables
  corrigo.py HOST dump  [GROUP]          read all readable variables
```

```bash
# Read the current ventilation mode
python3 corrigo.py 192.168.100.58 read "Mode (actual)"

# Read outdoor and supply temperature
python3 corrigo.py 192.168.100.58 read "Outdoor temperature" "Supply temperature"

# Set the supply air setpoint to 22 °C
python3 corrigo.py 192.168.100.58 write "Active supply setpoint" 22.0

# List all variables containing "fan"
python3 corrigo.py 192.168.100.58 list fan

# Dump all supply air readings
python3 corrigo.py 192.168.100.58 dump "Supply Air"

# JSON output (for scripting)
python3 corrigo.py 192.168.100.58 read "Mode (actual)" --json
```

---

## Home Assistant integration

A [HACS](https://hacs.xyz) integration that exposes all Corrigo E variables as Home Assistant entities, with polling and write support.

### Installation via HACS

1. In Home Assistant, open **HACS → Integrations**
2. Click the three-dot menu (⋮) → **Custom repositories**
3. Add `https://github.com/merbanan/EXOlink` with category **Integration**
4. Click **Download** on the Regin Corrigo E card
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration** and search for **Regin Corrigo E**

### Configuration

| Field | Default | Description |
|---|---|---|
| Host | — | Controller IP address or hostname |
| TCP port | 26486 | EXOline-TCP port |
| End Layer Address | 30 | Controller node address on the bus |
| Scan interval | 30 s | How often to poll the controller |

The End Layer Address (ELA) identifies the controller on the RS-485 bus. The factory default is **30**. Leave it unchanged unless your installer has configured a different address.

### Entities

The integration creates entities for all variables in `CorrigoEVentilation.variables`:

| Variable type | Access | HA platform |
|---|---|---|
| Real / Integer | Read-only | `sensor` |
| Logic (bool) | Read-only | `binary_sensor` |
| Index / Enum | Read-only | `sensor` (string state) |
| Real / Integer | Read-write | `number` |
| Index / Enum | Read-write | `select` |
| Logic (bool) | Read-write | `switch` |

A small set of key sensors is enabled by default (current mode, outdoor temperature, supply and extract temperature, active supply setpoint). All other entities start disabled and can be enabled individually under the device page.

---

## Protocol

EXOlink implements the EXOline-TCP protocol used by Regin Corrigo E controllers. See `EXOline-specification.md` for the full protocol reference and `variable-specification.md` for variable addressing details.
