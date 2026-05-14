"""Data update coordinator for Regin Corrigo E."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_ELA, CONF_SCAN_INTERVAL, DOMAIN
from .libexolink import EXOConnectionError, EXOlink, EXONakError
from .variable_db import VarRecord

_LOGGER = logging.getLogger(__name__)


class CorrigoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        variables: list[VarRecord],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
        )
        self.host: str = entry.data[CONF_HOST]
        self._port: int = entry.data[CONF_PORT]
        self._ela: int = entry.data[CONF_ELA]
        self._variables = variables
        self._client: EXOlink | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except EXOConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

    def _connect(self) -> None:
        client = EXOlink(self.host, port=self._port, ela=self._ela)
        client.connect()
        self._client = client

    def _fetch(self) -> dict[str, Any]:
        if self._client is None:
            self._connect()

        results: dict[str, Any] = {}
        for var in self._variables:
            try:
                results[var.ref] = self._client.read(var.ref)
            except EXONakError:
                results[var.ref] = None  # Not available on this controller
            except EXOConnectionError:
                self._client = None
                raise

        return results

    def write(self, ref: str, value: Any) -> None:
        """Write a value synchronously (call via async_add_executor_job)."""
        if self._client is None:
            self._connect()
        self._client.write(ref, value)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
