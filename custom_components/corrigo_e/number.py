"""Number platform for Regin Corrigo E (writable R/I variables)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
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
from .variable_db import VarRecord

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

_UNIT_RANGE: dict[str, tuple[float, float]] = {
    "°C": (-50.0, 100.0),
    "Pa": (0.0, 2000.0),
    "m3/h": (0.0, 5000.0),
    "%": (0.0, 100.0),
    "RH": (0.0, 100.0),
    "% RH": (0.0, 100.0),
    "ppm": (0.0, 5000.0),
    "s": (0.0, 3600.0),
    "kW": (0.0, 500.0),
    "A": (0.0, 100.0),
}


def _step(var: VarRecord) -> float:
    if var.datatype == "I":
        return 1.0
    if var.fmt is not None:
        return 10.0 ** (-var.fmt) if var.fmt > 0 else 1.0
    return 0.1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CorrigoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        CorrigoNumber(coordinator, entry, var)
        for var in coordinator._variables
        if var.rw and var.datatype in ("R", "I")
    )


class CorrigoNumber(CoordinatorEntity[CorrigoCoordinator], NumberEntity):
    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: CorrigoCoordinator,
        entry: ConfigEntry,
        var: VarRecord,
    ) -> None:
        super().__init__(coordinator)
        self._var = var
        self._attr_unique_id = f"{entry.entry_id}_{var.ref.replace(',', '_')}"
        subsection = var.group.rsplit(">", 1)[-1].strip()
        self._attr_name = f"{subsection} {var.name}"
        self._attr_entity_registry_enabled_default = var.ref in DEFAULT_ENABLED_REFS
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Corrigo E ({coordinator.host})",
            manufacturer="Regin",
            model="Corrigo E",
        )

        unit = var.unit or None
        self._attr_native_unit_of_measurement = _HA_UNIT.get(unit, unit) if unit else None
        lo, hi = _UNIT_RANGE.get(unit, (-32767.0, 32767.0)) if unit else (-32767.0, 32767.0)
        self._attr_native_min_value = lo
        self._attr_native_max_value = hi
        self._attr_native_step = _step(var)

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._var.ref)
        if value is None:
            return None
        if isinstance(value, float) and self._var.fmt is not None:
            return round(value, self._var.fmt)
        return float(value)

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None and \
               self.coordinator.data.get(self._var.ref) is not None

    async def async_set_native_value(self, value: float) -> None:
        typed = int(value) if self._var.datatype == "I" else value
        await self.hass.async_add_executor_job(self.coordinator.write, self._var.ref, typed)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, self._var.ref: typed}
        )
