"""Sensor platform for Regin Corrigo E."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_ENABLED_REFS, DOMAIN
from .coordinator import CorrigoCoordinator
from .variable_db import VarRecord, compute_entity_names

_HA_UNIT: dict[str, str | None] = {
    "°C": UnitOfTemperature.CELSIUS,
    "Pa": UnitOfPressure.PA,
    "m3/h": UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    "kW": UnitOfPower.KILO_WATT,
    "A": UnitOfElectricCurrent.AMPERE,
    "Hz": UnitOfFrequency.HERTZ,
    "h": UnitOfTime.HOURS,
    "%": PERCENTAGE,
    "RH": PERCENTAGE,
    "% RH": PERCENTAGE,
    "ppm": CONCENTRATION_PARTS_PER_MILLION,
    "kW/m3/s": "kW/m³/s",
}

_DEVICE_CLASS: dict[str, SensorDeviceClass | None] = {
    "°C": SensorDeviceClass.TEMPERATURE,
    "Pa": SensorDeviceClass.PRESSURE,
    "ppm": SensorDeviceClass.CO2,
    "kW": SensorDeviceClass.POWER,
    "A": SensorDeviceClass.CURRENT,
    "Hz": SensorDeviceClass.FREQUENCY,
    "h": SensorDeviceClass.DURATION,
    "RH": SensorDeviceClass.HUMIDITY,
    "% RH": SensorDeviceClass.HUMIDITY,
}

_IO_GROUPS = ("Input", "Output")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CorrigoCoordinator = hass.data[DOMAIN][entry.entry_id]
    vars = [v for v in coordinator._variables if not v.rw and v.datatype in ("R", "I", "X")]
    names = compute_entity_names(vars)
    async_add_entities(CorrigoSensor(coordinator, entry, var, names[var.ref]) for var in vars)


class CorrigoSensor(CoordinatorEntity[CorrigoCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CorrigoCoordinator,
        entry: ConfigEntry,
        var: VarRecord,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._var = var
        self._attr_unique_id = f"{entry.entry_id}_{var.ref.replace(',', '_')}"
        self._attr_name = name
        self._attr_entity_registry_enabled_default = var.ref in DEFAULT_ENABLED_REFS
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Corrigo E ({coordinator.host})",
            manufacturer="Regin",
            model="Corrigo E",
        )

        if any(var.group.startswith(g) for g in _IO_GROUPS):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        if var.datatype == "X":
            self._attr_native_unit_of_measurement = None
            self._attr_device_class = None
            self._attr_state_class = None
        else:
            unit = var.unit or None
            self._attr_native_unit_of_measurement = _HA_UNIT.get(unit, unit) if unit else None
            self._attr_device_class = _DEVICE_CLASS.get(unit) if unit else None
            if "run time" in var.name.lower():
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            elif unit:
                self._attr_state_class = SensorStateClass.MEASUREMENT
            if var.fmt is not None:
                self._attr_suggested_display_precision = var.fmt

    @property
    def native_value(self) -> float | int | str | None:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._var.ref)
        if value is None:
            return None
        if self._var.datatype == "X" and self._var.values:
            return self._var.values.get(int(value), str(value))
        if isinstance(value, float) and self._var.fmt is not None:
            return round(value, self._var.fmt)
        return value

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None and \
               self.coordinator.data.get(self._var.ref) is not None
