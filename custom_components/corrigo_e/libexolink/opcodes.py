"""EXOline opcode constants and lookup tables."""

# Read opcodes
RRL = 0xAE  # Local  Real
RIL = 0xAD  # Local  Integer
RLL = 0xAB  # Local  Logic
RXL = 0x2C  # Local  Index
RRP = 0xB6  # Parameter  Real
RIP = 0xB5  # Parameter  Integer
RLP = 0xB3  # Parameter  Logic
RXP = 0x34  # Parameter  Index
RRB = 0xBF  # Block  Real
RIB = 0x3E  # Block  Integer  (= EOM — escaped in frame)
RLB = 0xBC  # Block  Logic
RXB = 0x3D  # Block  Index    (= SOA — escaped in frame)
RSV = 0x8A  # String (read)

# Write opcodes
SRL = 0x2A  # Local  Real
SIL = 0x29  # Local  Integer
SLL = 0xA7  # Local  Logic
SXL = 0xA8  # Local  Index
SRP = 0x32  # Parameter  Real
SIP = 0x31  # Parameter  Integer
SLP = 0x2F  # Parameter  Logic
SXP = 0xB0  # Parameter  Index
SRB = 0x3B  # Block  Real
SIB = 0xBA  # Block  Integer
SLB = 0x38  # Block  Logic
SXB = 0xB9  # Block  Index
SSV = 0x85  # String (write)

# Special
POLL   = 0x98
MULCMD = 0xC8
GETV   = 0x10

# (scope, datatype) -> read opcode
READ_OPCODES: dict[tuple[str, str], int] = {
    ("L", "R"): RRL,
    ("L", "I"): RIL,
    ("L", "L"): RLL,
    ("L", "X"): RXL,
    ("V", "R"): RRP,
    ("V", "I"): RIP,
    ("V", "L"): RLP,
    ("V", "X"): RXP,
    ("B", "R"): RRB,
    ("B", "I"): RIB,
    ("B", "L"): RLB,
    ("B", "X"): RXB,
}

# (scope, datatype) -> write opcode
WRITE_OPCODES: dict[tuple[str, str], int] = {
    ("L", "R"): SRL,
    ("L", "I"): SIL,
    ("L", "L"): SLL,
    ("L", "X"): SXL,
    ("V", "R"): SRP,
    ("V", "I"): SIP,
    ("V", "L"): SLP,
    ("V", "X"): SXP,
    ("B", "R"): SRB,
    ("B", "I"): SIB,
    ("B", "L"): SLB,
    ("B", "X"): SXB,
}
