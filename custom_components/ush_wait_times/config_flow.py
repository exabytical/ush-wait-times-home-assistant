"""Config flow for Universal Studios Hollywood wait times."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.selector import SelectOptionDict, SelectSelectorMode

from .api import async_fetch_attractions
from .const import CONF_ATTRACTIONS, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=900)
        )
    }
)


class UshWaitTimeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for USH wait times."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        """Return the options flow handler."""
        return UshWaitTimeOptionsFlow()

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        return self.async_create_entry(title="USH Wait Times", data=user_input)


class UshWaitTimeOptionsFlow(OptionsFlow):
    """Handle options for USH wait times."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage ride selection options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={CONF_ATTRACTIONS: user_input.get(CONF_ATTRACTIONS) or []},
            )

        errors: dict[str, str] = {}
        try:
            attractions = await async_fetch_attractions(self.hass)
        except Exception as err:
            _LOGGER.exception("Failed to fetch attractions for options flow")
            errors["base"] = "cannot_connect"
            attractions = []

        attraction_options = [
            SelectOptionDict(
                value=attraction["wait_time_attraction_id"],
                label=attraction["name"],
            )
            for attraction in sorted(attractions, key=lambda item: item["name"].lower())
        ]
        current = self.config_entry.options.get(CONF_ATTRACTIONS, [])

        schema = vol.Schema(
            {
                vol.Optional(CONF_ATTRACTIONS): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=attraction_options,
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    ),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                schema,
                {CONF_ATTRACTIONS: current},
            ),
            errors=errors,
        )
