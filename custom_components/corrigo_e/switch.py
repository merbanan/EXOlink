"""Switch platform for Regin Corrigo E (writable L/logic variables)."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_ENABLED_REFS, DOMAIN
from .coordinator import CorrigoCoordinator
from .variable_db import VarRecord


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CorrigoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        CorrigoSwitch(coordinator, entry, var)
        for var in coordinator._variables
        if var.rw and var.datatype == "L"
    )


class CorrigoSwitch(CoordinatorEntity[CorrigoCoordinator], SwitchEntity):
    _attr_has_entity_name = True
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

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._var.ref)
        if value is None:
            return None
        return bool(value)

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None and \
               self.coordinator.data.get(self._var.ref) is not None

    async def async_turn_on(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(self.coordinator.write, self._var.ref, True)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, self._var.ref: True}
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(self.coordinator.write, self._var.ref, False)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, self._var.ref: False}
        )
