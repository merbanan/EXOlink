"""Select platform for Regin Corrigo E (writable X/index variables with enum labels)."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_ENABLED_REFS, DOMAIN
from .coordinator import CorrigoCoordinator
from .variable_db import VarRecord, compute_entity_names


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CorrigoCoordinator = hass.data[DOMAIN][entry.entry_id]
    vars = [v for v in coordinator._variables if v.rw and v.datatype == "X" and v.values]
    names = compute_entity_names(vars)
    async_add_entities(CorrigoSelect(coordinator, entry, var, names[var.ref]) for var in vars)


class CorrigoSelect(CoordinatorEntity[CorrigoCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

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
        self._attr_options = list(var.values.values())
        # Reverse map: label → index
        self._label_to_idx: dict[str, int] = {v: k for k, v in var.values.items()}

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._var.ref)
        if value is None:
            return None
        return self._var.values.get(int(value))

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None and \
               self.coordinator.data.get(self._var.ref) is not None

    async def async_select_option(self, option: str) -> None:
        idx = self._label_to_idx[option]
        await self.hass.async_add_executor_job(self.coordinator.write, self._var.ref, idx)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, self._var.ref: idx}
        )
