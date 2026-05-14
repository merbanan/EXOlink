DOMAIN = "corrigo_e"

CONF_ELA = "ela"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_PORT = 26486
DEFAULT_ELA = 30
DEFAULT_SCAN_INTERVAL = 30

PLATFORMS = ["sensor", "binary_sensor", "number", "select", "switch"]

# Refs enabled as entities by default; everything else starts disabled.
DEFAULT_ENABLED_REFS: frozenset[str] = frozenset({
    "V,3,0x1E9,X",  # Mode (actual) — current ventilation mode
    "V,3,0x084,R",  # Outdoor temperature
    "V,3,0x087,R",  # Supply temperature
    "V,3,0x08A,R",  # Extract temperature
    "V,2,0xE11,R",  # Active supply setpoint
    "V,2,0x321,X",  # Ventilation Unit Mode setpoint
})
