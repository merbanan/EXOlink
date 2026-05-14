"""Config flow for Regin Corrigo E."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import CONF_ELA, CONF_SCAN_INTERVAL, DEFAULT_ELA, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN
from .libexolink import EXOConnectionError, EXOlink


def _test_connection(host: str, port: int, ela: int) -> None:
    with EXOlink(host, port=port, ela=ela) as ctrl:
        ctrl.poll()


class CorrigoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self.hass.async_add_executor_job(
                    _test_connection,
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_ELA],
                )
            except EXOConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                uid = f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_ELA]}"
                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Corrigo E ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_ELA, default=DEFAULT_ELA): int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }),
            errors=errors,
        )
