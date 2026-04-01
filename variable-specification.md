# Corrigo E Ventilation — Variable Specification

This specification covers the **Corrigo E**, an air handling controller by Regin AB.

## Fields

| Field | Description |
|-------|-------------|
| **Variable Ref** | `ln,cell,type` — Line number (ln), cell address (cell), and data type (type). Prefix with `V,` in EXOline commands. ln=2: setpoint/command (R/W); ln=3: actual/status (R); ln=43: time channel. |
| **Type** | EXOline data type: **Real** = 32-bit IEEE 754 float; **Index** = uint8 enumeration; **Logic** = uint8 boolean (0/1). |
| **Access** | **R** = read-only; **R/W** = read and write. |
| **Unit** | Engineering unit for Real-type values. `—` = dimensionless or not applicable. |
| **Format** | Number of decimal places to display. `—` = not applicable. |
| **Values** | Comma-separated enum values (Index/Logic types) indexed from 0. |
| **Visibility condition** | `[visible if: ln,cell,type]` — Variable is only present when the referenced logic variable is true (1). |

---

# Manual/Auto — Manual Override Controls

## Ventilation Unit

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x321,X | Index | R/W | — | — | 0=Off; 1=Reduced Speed; 2=Normal Speed; 3=Auto |
| Mode (actual) | 3,0x1E9,X | Index | R | — | — | 0=Stopped; 1=Starting up; 2=Starting up; 3=Starting up; 4=Starting up; 5=Normal run; 6=Support control heat; 7=Support control cool; 8=CO2 run; 9=Night cooling; 10=Fullspeed stop; 11=Stopping fan; 12=Fire mode; 13=Recirculation run; 14=Defrosting |

## Supply Air Fan

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x322,X | Index | R/W | — | — | 0=Off; 1=Reduced Speed; 2=Normal Speed; 3=Auto |
| Normal speed | 3,0x1A7,L | Logic | R | — | — | 0=Off; 1=On |
| Reduced speed | 3,0x1A9,L | Logic | R | — | — | 0=Off; 1=On |

## Extract Air Fan

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x324,X | Index | R/W | — | — | 0=Off; 1=Reduced Speed; 2=Normal Speed; 3=Auto |
| Normal speed | 3,0x1A8,L | Logic | R | — | — | 0=Off; 1=On |
| Reduced speed | 3,0x1AA,L | Logic | R | — | — | 0=Off; 1=On |

## Exchanger Pump

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x32B,X | Index | R/W | — | — | [visible if: V,3,0x466,L] 0=Off; 1=On; 2=Auto |
| Pump | 3,0x144,L | Logic | R | — | — | [visible if: V,3,0x466,L] 0=Off; 1=On |

## Heater Pump

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x32A,X | Index | R/W | — | — | [visible if: V,3,0x465,L] 0=Off; 1=On; 2=Auto |
| Pump | 3,0x143,L | Logic | R | — | — | [visible if: V,3,0x465,L] 0=Off; 1=On |

## Cooler Pump

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x32C,X | Index | R/W | — | — | [visible if: V,3,0x467,L] 0=Off; 1=On; 2=Auto |
| Pump | 3,0x145,L | Logic | R | — | — | [visible if: V,3,0x467,L] 0=Off; 1=On |

## Fire Damper

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x32D,X | Index | R/W | — | — | [visible if: V,3,0x469,L] 0=Closed; 1=Open; 2=Auto |
| Damper | 3,0x1AE,L | Logic | R | — | — | [visible if: V,3,0x469,L] 0=Closed; 1=Open |

## Recycle Air Damper

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x32E,X | Index | R/W | — | — | [visible if: V,3,0x47E,L] 0=Closed; 1=Open; 2=Auto |
| Damper | 3,0x1B7,L | Logic | R | — | — | [visible if: V,3,0x47E,L] 0=Closed; 1=Open |

## Fresh Air Damper

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x32F,X | Index | R/W | — | — | [visible if: V,3,0x47F,L] 0=Closed; 1=Open; 2=Auto |
| Damper | 3,0x1B8,L | Logic | R | — | — | [visible if: V,3,0x47F,L] 0=Closed; 1=Open |

## Exhaust Air Damper

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x330,X | Index | R/W | — | — | [visible if: V,3,0x480,L] 0=Closed; 1=Open; 2=Auto |
| Damper | 3,0x1B9,L | Logic | R | — | — | [visible if: V,3,0x480,L] 0=Closed; 1=Open |

## Humidity/Dehumidity

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0x6E7,X | Index | R/W | — | — | [visible if: V,3,0x468,L] 0=Off; 1=On; 2=Auto |
| Output | 3,0x1CC,L | Logic | R | — | — | [visible if: V,3,0x468,L] 0=Off; 1=On |

## Pretreatment

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0xB10,X | Index | R/W | — | — | 0=Closed; 1=Open; 2=Auto |
| Output | 3,0x1D2,L | Logic | R | — | — | 0=Off; 1=On |

## Y4 Extra Sequence

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0xE52,X | Index | R/W | — | — | [visible if: V,3,0x4A9,L] 0=Off; 1=On; 2=Auto |
| Output | 3,0x1D9,L | Logic | R | — | — | [visible if: V,3,0x4A9,L] 0=Off; 1=On |

## Y5 Extra Sequence

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Mode | 2,0xE53,X | Index | R/W | — | — | [visible if: V,3,0x516,L] 0=Off; 1=On; 2=Auto |
| Output | 3,0x1DA,L | Logic | R | — | — | [visible if: V,3,0x516,L] 0=Off; 1=On |

# SetPointLeft — Setpoints (left panel)

## General

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Ventilation mode | 3,0x1E9,X | Index | R | — | — | 0=Stopped; 1=Starting up; 2=Starting up; 3=Starting up; 4=Starting up; 5=Normal run; 6=Support control heat; 7=Support control cool; 8=CO2 run; 9=Night cooling; 10=Fullspeed stop; 11=Stopping fan; 12=Fire mode; 13=Recirculation run; 14=Defrosting |
| Outdoor temperature | 3,0x084,R | Real | R | °C | 1 | [visible if: V,3,0x4B7,L] |
| Intake air temp | 3,0x0BD,R | Real | R | °C | 1 | [visible if: V,3,0x50B,L] |
| Timechannel normal speed | 43,0x00C,L | Logic | R | — | — | 0=Off, 1=On |
| Timechannel reduced speed | 43,0x00D,L | Logic | R | — | — | 0=Off, 1=On |
| Extended operation normal speed | 3,0x119,L | Logic | R | — | — | 0=Off, 1=On |
| Extended operation reduced speed | 3,0x11A,L | Logic | R | — | — | 0=Off, 1=On |
| Extract temperature | 3,0x08A,R | Real | R | °C | 1 | [visible if: V,3,0x448,L] |
| Room temperature 1 | 3,0x08D,R | Real | R | °C | 1 | [visible if: V,3,0x458,L] |
| Room temperature 2 | 3,0x090,R | Real | R | °C | 1 | [visible if: V,3,0x45A,L] |
| Extract temperature | 3,0x093,R | Real | R | °C | 1 | [visible if: V,3,0x45B,L] |
| Extra sensor 1 | 3,0x096,R | Real | R | °C | 1 | [visible if: V,3,0x464,L] |
| Extra sensor 2 | 3,0x0C0,R | Real | R | °C | 1 | [visible if: V,3,0x505,L] |
| Extra sensor 3 | 3,0x0C3,R | Real | R | °C | 1 | [visible if: V,3,0x506,L] |
| Extra sensor 4 | 3,0x0C6,R | Real | R | °C | 1 | [visible if: V,3,0x507,L] |
| Extra sensor 5 | 3,0x0C9,R | Real | R | °C | 1 | [visible if: V,3,0x508,L] |
| Extra flow SAF | 3,0x10B,R | Real | R | m3/h | 1 | [visible if: V,3,0x509,L] |
| Extra flow EAF | 3,0x10E,R | Real | R | m3/h | 1 | [visible if: V,3,0x50A,L] |
| Heat exchanger efficiency | 3,0x1E6,R | Real | R | % | 1 | [visible if: V,3,0x499,L] |
| Supply Air Fan run time | 3,0x1EA,R | Real | R | h | — | — |
| Extract Air Fan run time | 3,0x1ED,R | Real | R | h | — | — |

## Supply Air

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Supply temperature | 3,0x087,R | Real | R | °C | 1 | — |
| Supply setpoint | 2,0x210,R | Real | R/W | °C | 1 | [visible if: V,3,0x446,L] |
| Supply setpoint | 3,0x35A,R | Real | R | °C | 1 | [visible if: V,3,0x496,L] |
| Active supply setpoint | 2,0xE11,R | Real | R/W | °C | 1 | — |
| Max supply setpoint | 2,0x225,R | Real | R/W | °C | 1 | [visible if: V,3,0x50D,L] |
| Min supply setpoint | 2,0x228,R | Real | R/W | °C | 1 | [visible if: V,3,0x50D,L] |
| Controller Output | 3,0x387,R | Real | R | % | — | — |
| Outdoortemp. X1, Supply Setpoint Y1 | 2,0x630,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |
| Outdoortemp. X2, Supply Setpoint Y2 | 2,0x633,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |
| Outdoortemp. X3, Supply Setpoint Y3 | 2,0x636,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |
| Outdoortemp. X4, Supply Setpoint Y4 | 2,0x639,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |
| Outdoortemp. X5, Supply Setpoint Y5 | 2,0x63C,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |
| Outdoortemp. X6, Supply Setpoint Y6 | 2,0x63F,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |
| Outdoortemp. X7, Supply Setpoint Y7 | 2,0x642,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |
| Outdoortemp. X8, Supply Setpoint Y8 | 2,0x645,R | Real | R/W | °C | 1 | [visible if: V,3,0x447,L] |

## Extra control unit

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Temperatur extra control unit | 3,0x0AE,R | Real | R | °C | 1 | [visible if: V,3,0x49B,L] |
| Setpoint | 2,0x5F8,R | Real | R/W | °C | 1 | [visible if: V,3,0x49B,L] |
| Controller Output | 3,0x3A2,R | Real | R | % | 0 | [visible if: V,3,0x49B,L] |


# SetPointRight — Setpoints (right panel)

## Extract Air

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Extract temperature | 3,0x08A,R | Real | R | °C | 1 | [visible if: V,3,0x448,L] |
| Controller Output | 3,0x38A,R | Real | R | °C | 1 | [visible if: V,3,0x448,L] |
| Extract setpoint | 2,0x213,R | Real | R/W | °C | 1 | [visible if: V,3,0x448,L] |

## Frequency controlled Supply Air Fan

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Supply Air Fan pressure | 3,0x099,R | Real | R | Pa | — | [visible if: V,3,0x44F,L] |
| Supply Air Fan air flow | 3,0x102,R | Real | R | m3/h | — | [visible if: V,3,0x450,L] |
| Frequency (Vacon) | 3,0x3B8,R | Real | R | Hz | — | [visible if: V,3,0x504,L] |
| Current (Vacon) | 3,0x3C0,R | Real | R | A | — | [visible if: V,3,0x504,L] |
| Power (Vacon) | 3,0x3C6,R | Real | R | kW | — | [visible if: V,3,0x504,L] |
| Frequency EAF (Vacon) | 3,0x5E9,R | Real | R | Hz | — | [visible if: V,3,0x514,L] |
| Current EAF (Vacon) | 3,0x5EF,R | Real | R | A | — | [visible if: V,3,0x514,L] |
| Power EAF (Vacon) | 3,0x5F5,R | Real | R | kW | — | [visible if: V,3,0x514,L] |
| Controller Output | 3,0x38D,R | Real | R | % | — | [visible if: V,3,0x44E,L] |
| Actual Setpoint Compensation | 3,0x1FE,R | Real | R | Pa | — | [visible if: V,3,0x44F,L] |
| Actual Setpoint Compensation | 3,0x1FE,R | Real | R | m3/h | — | [visible if: V,3,0x450,L] |
| Actual Setpoint Compensation | 3,0x1FE,R | Real | R | % | — | [visible if: V,3,0x451,L] |
| Supply Air Fan normal speed setpoint | 2,0x216,R | Real | R/W | Pa | — | [visible if: V,3,0x44F,L] |
| Supply Air Fan reduced speed setpoint | 2,0x219,R | Real | R/W | Pa | — | [visible if: V,3,0x44F,L] |
| Supply Air Fan normal speed setpoint | 2,0x24A,R | Real | R/W | m3/h | — | [visible if: V,3,0x450,L] |
| Supply Air Fan reduced speed setpoint | 2,0x24D,R | Real | R/W | m3/h | — | [visible if: V,3,0x450,L] |
| Supply Air Fan output normal speed | 2,0x235,R | Real | R/W | % | — | [visible if: V,3,0x451,L] |
| Supply Air Fan output reduced speed | 2,0x238,R | Real | R/W | % | — | [visible if: V,3,0x451,L] |
| Min output setpoint | 2,0xE2B,R | Real | R/W | — | — | [visible if: V,2,0x267,L] |

## Frequency controlled Extract Air Fan

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Extract Air Fan pressure | 3,0x09C,R | Real | R | Pa | — | [visible if: V,3,0x44F,L] |
| Extract Air Fan air flow | 3,0x108,R | Real | R | m3/h | — | [visible if: V,3,0x450,L] |
| Max supply setpoint | 3,0x105,R | Real | R | m3/h | — | [visible if: V,3,0x4C8,L] |
| Frequency (Vacon) | 3,0x3FC,R | Real | R | Hz | — | [visible if: V,3,0x504,L] |
| Current (Vacon) | 3,0x402,R | Real | R | A | — | [visible if: V,3,0x504,L] |
| Power (Vacon) | 3,0x408,R | Real | R | kW | — | [visible if: V,3,0x504,L] |
| Frequency EAF (Vacon) | 3,0x62B,R | Real | R | Hz | — | [visible if: V,3,0x514,L] |
| Current EAF (Vacon) | 3,0x631,R | Real | R | A | — | [visible if: V,3,0x514,L] |
| Power EAF (Vacon) | 3,0x637,R | Real | R | kW | — | [visible if: V,3,0x514,L] |
| Controller Output | 3,0x390,R | Real | R | % | — | [visible if: V,3,0x44E,L] |
| Actual Setpoint Compensation | 3,0x1FE,R | Real | R | Pa | — | [visible if: V,3,0x44F,L] |
| Actual Setpoint Compensation | 3,0x1FE,R | Real | R | % | — | [visible if: V,3,0x451,L] |
| Supply Air Fan normal speed setpoint | 2,0x21C,R | Real | R/W | Pa | — | [visible if: V,3,0x44F,L] |
| Supply Air Fan reduced speed setpoint | 2,0x21F,R | Real | R/W | Pa | — | [visible if: V,3,0x44F,L] |
| Supply Air Fan normal speed setpoint | 2,0x250,R | Real | R/W | m3/h | — | [visible if: V,3,0x450,L] |
| Supply Air Fan reduced speed setpoint | 2,0x253,R | Real | R/W | m3/h | — | [visible if: V,3,0x450,L] |
| Supply Air Fan output normal speed | 2,0x23B,R | Real | R/W | % | — | [visible if: V,3,0x451,L] |
| Supply Air Fan output reduced speed | 2,0x23E,R | Real | R/W | % | — | [visible if: V,3,0x451,L] |
| Min output setpoint | 2,0xE2E,R | Real | R/W | — | — | [visible if: V,2,0x267,L] |

## Outdoor Comp. Curve Pressure/Flow Setpoint

## Outdoor Comp. Curve Pressure/Flow Setpoint

## Outdoor Comp. Curve Pressure/Flow Setpoint

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Outdoor temperature for lower point | 2,0x613,R | Real | R/W | °C | 1 | [visible if: V,3,0x452,L] |
| Outdoor temperature for lower point | 2,0x613,R | Real | R/W | °C | 1 | [visible if: V,3,0x453,L] |
| Outdoor temperature for lower point | 2,0x613,R | Real | R/W | °C | 1 | [visible if: V,3,0x451,L] |
| Pressere compensation at lower point | 2,0x5AC,R | Real | R/W | Pa | — | [visible if: V,3,0x452,L] |
| Pressere compensation at lower point | 2,0x5AC,R | Real | R/W | m3/h | — | [visible if: V,3,0x453,L] |
| Pressere compensation at lower point | 2,0x5AC,R | Real | R/W | % | — | [visible if: V,3,0x451,L] |
| Outdoor temperature for higher point | 2,0x5B5,R | Real | R/W | °C | 1 | [visible if: V,3,0x452,L] |
| Outdoor temperature for higher point | 2,0x5B5,R | Real | R/W | °C | 1 | [visible if: V,3,0x453,L] |
| Outdoor temperature for higher point | 2,0x5B5,R | Real | R/W | % | — | [visible if: V,3,0x451,L] |
| Pressure compensation at higer point | 2,0x5B2,R | Real | R/W | Pa | — | [visible if: V,3,0x452,L] |
| Pressure compensation at higer point | 2,0x5B2,R | Real | R/W | m3/h | — | [visible if: V,3,0x453,L] |
| Pressure compensation at higer point | 2,0x5B2,R | Real | R/W | % | — | [visible if: V,3,0x451,L] |
| Pressure/flow compensation only Supply Air Fan | 2,0x5B8,L | Logic | R/W | — | — | 0=Off, 1=On [visible if: V,3,0x452,L] |
| Pressure/flow compensation only Supply Air Fan | 2,0x5B8,L | Logic | R/W | — | — | 0=Off, 1=On [visible if: V,3,0x453,L] |
| Pressure/flow compensation only Supply Air Fan | 2,0x5B8,L | Logic | R/W | — | — | 0=Off, 1=On [visible if: V,3,0x451,L] |

## Room

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Room temperature | 3,0x0FC,R | Real | R | °C | 1 | [visible if: V,3,0x449,L] |
| Controller Output | 3,0x399,R | Real | R | % | — | [visible if: V,3,0x449,L] |
| Room setpoint | 2,0x30F,R | Real | R/W | °C | 1 | [visible if: V,3,0x449,L] |

## Support Control

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Room temperature | 3,0x0FC,R | Real | R | °C | 1 | [visible if: V,3,0x44A,L] |
| Start heating at room temp | 2,0x28A,R | Real | R/W | °C | 1 | [visible if: V,3,0x44A,L] |
| Stop heating at room temp | 2,0x28D,R | Real | R/W | °C | 1 | [visible if: V,3,0x44A,L] |
| Start cooling at room temp | 2,0x290,R | Real | R/W | °C | 1 | [visible if: V,3,0x44A,L] |
| Stop cooling at room temp | 2,0x294,R | Real | R/W | °C | 1 | [visible if: V,3,0x44A,L] |

## CO2

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| CO2 sensor | 3,0x0A5,R | Real | R | ppm | — | [visible if: V,3,0x460,L] |
| Controller Output | 3,0x396,R | Real | R | % | — | [visible if: V,3,0x460,L] |
| CO2 setpoint | 2,0x222,R | Real | R/W | ppm | — | [visible if: V,3,0x460,L] |

## CO2

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| CO2 sensor | 3,0x0A5,R | Real | R | ppm | — | [visible if: V,3,0x498,L] |
| Start reduced speed at CO2 level | 2,0x280,R | Real | R/W | ppm | — | [visible if: V,3,0x498,L] |
| Start normal speed at CO2 level | 2,0x283,R | Real | R/W | ppm | — | [visible if: V,3,0x498,L] |
| Stop at CO2 level difference | 2,0x286,R | Real | R/W | ppm | — | [visible if: V,3,0x498,L] |

## Frost Protection

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Frost protection temperature | 3,0x0A2,R | Real | R | °C | 1 | [visible if: V,3,0x45F,L] |
| Controller Output | 3,0x393,R | Real | R | % | — | [visible if: V,3,0x45F,L] |
| Setpoint when stopped | 2,0x344,R | Real | R/W | °C | 1 | [visible if: V,3,0x45F,L] |
| P-band when running | 2,0x348,R | Real | R/W | °C | 1 | [visible if: V,3,0x45F,L] |

## Deicing

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Deicing temperature | 3,0x09F,R | Real | R | °C | 1 | [visible if: V,3,0x45E,L] |
| Controller Output | 3,0x39C,R | Real | R | % | — | [visible if: V,3,0x45E,L] |
| Setpoint | 2,0x2A3,R | Real | R/W | °C | 1 | [visible if: V,3,0x45E,L] |
| Hysteresis | 2,0x2A6,R | Real | R/W | °C | 1 | [visible if: V,3,0x45E,L] |

## Humidity

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Humidity room | 3,0x0A8,R | Real | R | % | — | [visible if: V,3,0x461,L] |
| Controller Output | 3,0x39F,R | Real | R | % | — | [visible if: V,3,0x468,L] |
| Humidity Duct | 3,0x0AB,R | Real | R | % | — | [visible if: V,3,0x462,L] |
| Setpoint | 2,0x2AE,R | Real | R/W | RH | — | [visible if: V,3,0x468,L] |
| Max humidity in duct | 2,0x2B1,R | Real | R/W | RH | — | [visible if: V,3,0x462,L] |

## Recycling

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Recirkulation setpoint | 2,0x5FC,R | Real | R/W | °C | 1 | [visible if: V,3,0x49C,L] |
| Offset supply setpoint when recirculation | 2,0xB2D,R | Real | R/W | °C | 0 | [visible if: V,3,0x49C,L] |
| Offset SAF | 2,0x604,R | Real | R/W | — | 0 | [visible if: V,3,0x49C,L] |

## Extra Comp. Curve Pressure/Flow Setpoint

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Temperature sensor for pressure compensation | 2,0xB2C,X | Index | R | — | — | 0=-; 1=-; 2=Supplytemp; 3=Extracttemp; 4=Roomtemp1; 5=Roomtemp2 [visible if: V,3,0x515,L] |
| Outdoor temperature for lower point | 2,0xB1C,R | Real | R/W | °C | 0 | [visible if: V,3,0x515,L] |
| Outdoor temperature for middle point | 2,0xB22,R | Real | R/W | °C | 0 | [visible if: V,3,0x515,L] |
| Outdoor temperature for higher point | 2,0xB28,R | Real | R/W | °C | 0 | [visible if: V,3,0x515,L] |
| Pressere compensation at lower point | 2,0xB19,R | Real | R/W | Pa | 0 | [visible if: V,3,0x44F,L] |
| Pressere compensation at middle point | 2,0xB1F,R | Real | R/W | Pa | 0 | [visible if: V,3,0x44F,L] |
| Pressure compensation at higer point | 2,0xB25,R | Real | R/W | Pa | 0 | [visible if: V,3,0x44F,L] |
| Pressere compensation at lower point | 2,0xB19,R | Real | R/W | m3/h | 0 | [visible if: V,3,0x450,L] |
| Pressere compensation at middle point | 2,0xB1F,R | Real | R/W | m3/h | 0 | [visible if: V,3,0x450,L] |
| Pressure compensation at higer point | 2,0xB25,R | Real | R/W | m3/h | 0 | [visible if: V,3,0x450,L] |
| Pressere compensation at lower point | 2,0xB19,R | Real | R/W | % | 0 | [visible if: V,3,0x451,L] |
| Pressere compensation at middle point | 2,0xB1F,R | Real | R/W | % | 0 | [visible if: V,3,0x451,L] |
| Pressure compensation at higer point | 2,0xB25,R | Real | R/W | % | 0 | [visible if: V,3,0x451,L] |
| Pressure/flow compensation only Supply Air Fan | 2,0xB2B,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x44E,L] |

## Controller output comp. Pressure/Flow Setpoint

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| Controller output compensating | 2,0xB53,X | Index | R/W | — | — | 0=Not active; 1=Increase pressure/flow; 2=Decrease pressure/flow [visible if: V,3,0x515,L] |
| Controller output for Comp.=0 at cooling demand | 2,0xB54,R | Real | R/W | % | 0 | [visible if: V,3,0x515,L] |
| Controller output for Comp.=100 at cooling demand | 2,0xB57,R | Real | R/W | % | 0 | [visible if: V,3,0x515,L] |
| Reference value at cooling demand | 2,0xE25,R | Real | R/W | — | 0 | [visible if: V,3,0x515,L] |
| Controller output for Comp.=0 at heating demand | 2,0xB5A,R | Real | R/W | % | 0 | [visible if: V,3,0x515,L] |
| Controller output for Comp.=100 at heating demand | 2,0xB5D,R | Real | R/W | % | 0 | [visible if: V,3,0x515,L] |
| Reference value at heating demand | 2,0xE28,R | Real | R/W | — | 0 | [visible if: V,3,0x515,L] |

## SFP (Specific Fan Power)

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| SFP | 3,0x5D0,R | Real | R | kW/m3/s | 2 | [visible if: V,3,0x50E,L] |
| SFP day average | 3,0x5D3,R | Real | R | kW/m3/s | 2 | [visible if: V,3,0x50E,L] |
| SFP month average | 3,0x5D6,R | Real | R | kW/m3/s | 2 | [visible if: V,3,0x50E,L] |
| SFP month average | 3,0x5D6,R | Real | R | kW/m3/s | 2 | [visible if: V,3,0x50E,L] |
| Frequencer loss | 2,0xC79,R | Real | R | % | 0 | [visible if: V,3,0x50E,L] |


# Input — I/O Inputs

## Analog Inputs

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| AI1 | 3,0x009,R | Real | R | — | 1 | — |
| AI2 | 3,0x00C,R | Real | R | — | 1 | — |
| AI3 | 3,0x00F,R | Real | R | — | 1 | [visible if: V,3,0x49A,L] |
| AI4 | 3,0x012,R | Real | R | — | 1 | [visible if: V,3,0x49A,L] |
| UAI1 | 3,0x015,R | Real | R | — | 1 | [visible if: V,3,0x46C,L] |
| UAI2 | 3,0x018,R | Real | R | — | 1 | [visible if: V,3,0x46C,L] |
| UAI3 | 3,0x01B,R | Real | R | — | 1 | [visible if: V,3,0x46C,L] |
| UAI4 | 3,0x01E,R | Real | R | — | 1 | [visible if: V,3,0x46C,L] |
| Exp1AI1 | 3,0x021,R | Real | R | — | 1 | [visible if: V,3,0x4FE,L] |
| Exp1AI2 | 3,0x024,R | Real | R | — | 1 | [visible if: V,3,0x4FE,L] |
| Exp1AI3 | 3,0x027,R | Real | R | — | 1 | [visible if: V,3,0x4FF,L] |
| Exp1AI4 | 3,0x02A,R | Real | R | — | 1 | [visible if: V,3,0x4FF,L] |
| Exp1UAI1 | 3,0x02D,R | Real | R | — | 1 | [visible if: V,3,0x500,L] |
| Exp1UAI2 | 3,0x030,R | Real | R | — | 1 | [visible if: V,3,0x500,L] |
| Exp1UAI3 | 3,0x033,R | Real | R | — | 1 | [visible if: V,3,0x500,L] |
| Exp1UAI4 | 3,0x036,R | Real | R | — | 1 | [visible if: V,3,0x500,L] |
| Exp2AI1 | 3,0x039,R | Real | R | — | 1 | [visible if: V,3,0x501,L] |
| Exp2AI2 | 3,0x03C,R | Real | R | — | 1 | [visible if: V,3,0x501,L] |
| Exp2AI3 | 3,0x03F,R | Real | R | — | 1 | [visible if: V,3,0x502,L] |
| Exp2AI4 | 3,0x042,R | Real | R | — | 1 | [visible if: V,3,0x502,L] |
| Exp2UAI1 | 3,0x045,R | Real | R | — | 1 | [visible if: V,3,0x503,L] |
| Exp2UAI2 | 3,0x048,R | Real | R | — | 1 | [visible if: V,3,0x503,L] |
| Exp2UAI3 | 3,0x04B,R | Real | R | — | 1 | [visible if: V,3,0x503,L] |
| Exp2UAI4 | 3,0x04E,R | Real | R | — | 1 | [visible if: V,3,0x503,L] |
| Exp3UAI1 | 3,0x069,R | Real | R | — | 1 | [visible if: V,3,0x56C,L] |
| Exp3UAI2 | 3,0x06C,R | Real | R | — | 1 | [visible if: V,3,0x56C,L] |
| Exp3DIA | 3,0x06F,R | Real | R | — | 1 | [visible if: V,3,0x56C,L] |
| Exp3DIB | 3,0x072,R | Real | R | — | 1 | [visible if: V,3,0x56B,L] |
| Exp4UAI1 | 3,0x075,R | Real | R | — | 1 | [visible if: V,3,0x56E,L] |
| Exp4UAI2 | 3,0x078,R | Real | R | — | 1 | [visible if: V,3,0x56E,L] |
| Exp4DIA | 3,0x07B,R | Real | R | — | 1 | [visible if: V,3,0x56E,L] |
| Exp4DIB | 3,0x07E,R | Real | R | — | 1 | [visible if: V,3,0x56D,L] |
| Exp5UAI1 | 3,0x708,R | Real | R | — | 1 | [visible if: V,3,0x570,L] |
| Exp5UAI2 | 3,0x70B,R | Real | R | — | 1 | [visible if: V,3,0x570,L] |
| Exp5DIA | 3,0x70E,R | Real | R | — | 1 | [visible if: V,3,0x570,L] |
| Exp5DIB | 3,0x711,R | Real | R | — | 1 | [visible if: V,3,0x56F,L] |
| Exp6UAI1 | 3,0x714,R | Real | R | — | 1 | [visible if: V,3,0x572,L] |
| Exp6UAI2 | 3,0x717,R | Real | R | — | 1 | [visible if: V,3,0x572,L] |
| Exp6DIA | 3,0x71A,R | Real | R | — | 1 | [visible if: V,3,0x572,L] |
| Exp6DIB | 3,0x71D,R | Real | R | — | 1 | [visible if: V,3,0x571,L] |

## Digital Inputs

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| DI1 | 59,0x003,L | Logic | R | — | — | 0=Off, 1=On |
| DI2 | 59,0x004,L | Logic | R | — | — | 0=Off, 1=On |
| DI3 | 59,0x005,L | Logic | R | — | — | 0=Off, 1=On |
| DI4 | 59,0x006,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x49A,L] |
| DI5 | 59,0x007,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| DI6 | 59,0x008,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| DI7 | 59,0x009,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| DI8 | 59,0x00A,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| UDI1 | 59,0x00B,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| UDI2 | 59,0x00C,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| UDI3 | 59,0x00D,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| UDI4 | 59,0x00E,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| Exp1DI1 | 59,0x00F,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FE,L] |
| Exp1DI2 | 59,0x010,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FE,L] |
| Exp1DI3 | 59,0x011,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FE,L] |
| Exp1DI4 | 59,0x012,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FF,L] |
| Exp1DI5 | 59,0x013,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1DI6 | 59,0x014,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1DI7 | 59,0x015,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1DI8 | 59,0x016,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1UDI1 | 59,0x017,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1UDI2 | 59,0x018,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1UDI3 | 59,0x019,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1UDI4 | 59,0x01A,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp2DI1 | 59,0x01B,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x501,L] |
| Exp2DI2 | 59,0x01C,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x501,L] |
| Exp2DI3 | 59,0x01D,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x501,L] |
| Exp2DI4 | 59,0x01E,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x502,L] |
| Exp2DI5 | 59,0x01F,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2DI6 | 59,0x020,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2DI7 | 59,0x021,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2DI8 | 59,0x022,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2UDI1 | 59,0x023,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2UDI2 | 59,0x024,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2UDI3 | 59,0x025,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2UDI4 | 59,0x026,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp3UDI1 | 3,0x6D2,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x56C,L] |
| Exp3UDI2 | 3,0x6D3,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x56C,L] |
| Exp4UDI1 | 3,0x6D4,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x56E,L] |
| Exp4UDI2 | 3,0x6D5,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x56E,L] |
| Exp5UDI1 | 3,0x7B3,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x570,L] |
| Exp5UDI2 | 3,0x7B4,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x570,L] |
| Exp6UDI1 | 3,0x7B5,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x572,L] |
| Exp6UDI2 | 3,0x7B6,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x572,L] |


# Output — I/O Outputs

## Analog Outputs

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| AO1 | 59,0x80D,R | Real | R | — | 1 | — |
| AO2 | 59,0x810,R | Real | R | — | 1 | [visible if: V,3,0x49A,L] |
| AO3 | 59,0x813,R | Real | R | — | 1 | [visible if: V,3,0x49A,L] |
| AO4 | 59,0x816,R | Real | R | — | 1 | [visible if: V,3,0x46C,L] |
| AO5 | 59,0x819,R | Real | R | — | 1 | [visible if: V,3,0x46C,L] |
| Exp1AO1 | 59,0x81C,R | Real | R | — | 1 | [visible if: V,3,0x4FE,L] |
| Exp1AO2 | 59,0x81F,R | Real | R | — | 1 | [visible if: V,3,0x4FF,L] |
| Exp1AO3 | 59,0x822,R | Real | R | — | 1 | [visible if: V,3,0x4FF,L] |
| Exp1AO4 | 59,0x825,R | Real | R | — | 1 | [visible if: V,3,0x500,L] |
| Exp1AO5 | 59,0x828,R | Real | R | — | 1 | [visible if: V,3,0x500,L] |
| Exp2AO1 | 59,0x82B,R | Real | R | — | 1 | [visible if: V,3,0x501,L] |
| Exp2AO2 | 59,0x82E,R | Real | R | — | 1 | [visible if: V,3,0x502,L] |
| Exp2AO3 | 59,0x831,R | Real | R | — | 1 | [visible if: V,3,0x502,L] |
| Exp2AO4 | 59,0x834,R | Real | R | — | 1 | [visible if: V,3,0x503,L] |
| Exp2AO5 | 59,0x837,R | Real | R | — | 1 | [visible if: V,3,0x503,L] |

## Digital Outputs

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| DO1 | 59,0x437,L | Logic | R | — | — | 0=Off, 1=On |
| DO2 | 59,0x438,L | Logic | R | — | — | 0=Off, 1=On |
| DO3 | 59,0x439,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x49A,L] |
| DO4 | 59,0x43A,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x49A,L] |
| DO5 | 59,0x43B,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| DO6 | 59,0x43C,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| DO7 | 59,0x43D,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x46C,L] |
| Exp1DO1 | 59,0x43E,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FE,L] |
| Exp1DO2 | 59,0x43F,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FE,L] |
| Exp1DO3 | 59,0x440,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FF,L] |
| Exp1DO4 | 59,0x441,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x4FF,L] |
| Exp1DO5 | 59,0x442,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1DO6 | 59,0x443,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp1DO7 | 59,0x444,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x500,L] |
| Exp2DO1 | 59,0x445,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x501,L] |
| Exp2DO2 | 59,0x446,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x501,L] |
| Exp2DO3 | 59,0x447,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x502,L] |
| Exp2DO4 | 59,0x448,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x502,L] |
| Exp2DO5 | 59,0x449,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2DO6 | 59,0x44A,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |
| Exp2DO7 | 59,0x44B,L | Logic | R | — | — | 0=Off, 1=On [visible if: V,3,0x503,L] |


# Settings — Controller Settings

## Controller Settings

| Name | Variable Ref | Type | Access | Unit | Format | Values / Visibility condition |
|------|-------------|------|--------|------|--------|-------------------------------|
| P-band | 2,0x65A,R | Real | R/W | °C | — | — |
| I-time | 2,0x687,R | Real | R/W | s | — | — |
| P-band | 2,0x65D,R | Real | R/W | °C | — | [visible if: V,3,0x448,L] |
| I-time | 2,0x68A,R | Real | R/W | s | — | [visible if: V,3,0x448,L] |
| P-band pressure | 2,0x660,R | Real | R/W | Pa | — | [visible if: V,3,0x44F,L] |
| P-band flow | 2,0x258,R | Real | R/W | m3/h | — | [visible if: V,3,0x450,L] |
| I-time | 2,0x68D,R | Real | R/W | s | — | [visible if: V,3,0x44E,L] |
| Min utsignal | 2,0x732,R | Real | R/W | % | — | [visible if: V,3,0x44E,L] |
| P-band pressure | 2,0x663,R | Real | R/W | Pa | — | [visible if: V,3,0x44F,L] |
| P-band flow | 2,0x25B,R | Real | R/W | m3/h | — | [visible if: V,3,0x450,L] |
| I-time | 2,0x690,R | Real | R/W | s | — | [visible if: V,3,0x44E,L] |
| Min utsignal | 2,0x735,R | Real | R/W | % | — | [visible if: V,3,0x44E,L] |
| P-band | 2,0x66C,R | Real | R/W | °C | — | [visible if: V,3,0x449,L] |
| I-time | 2,0x699,R | Real | R/W | s | — | [visible if: V,3,0x449,L] |
| P-band | 2,0x669,R | Real | R/W | ppm | — | [visible if: V,3,0x497,L] |
| I-time | 2,0x696,R | Real | R/W | s | — | [visible if: V,3,0x497,L] |
| P-band | 2,0x666,R | Real | R/W | °C | — | [visible if: V,3,0x45F,L] |
| I-time | 2,0x693,R | Real | R/W | s | — | [visible if: V,3,0x45F,L] |
| P-band | 2,0x66F,R | Real | R/W | °C | — | [visible if: V,3,0x45E,L] |
| I-time | 2,0x69C,R | Real | R/W | s | — | [visible if: V,3,0x45E,L] |
| P-band | 2,0x672,R | Real | R/W | % RH | — | [visible if: V,3,0x468,L] |
| I-time | 2,0x69F,R | Real | R/W | s | — | [visible if: V,3,0x468,L] |
| P-band | 2,0x675,R | Real | R/W | °C | — | [visible if: V,3,0x49B,L] |
| I-time | 2,0x6A2,R | Real | R/W | s | — | [visible if: V,3,0x49B,L] |

