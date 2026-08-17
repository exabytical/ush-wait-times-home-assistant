"""Config flow for Universal Studios Hollywood wait times."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers import selector

from .api import async_fetch_attractions
from .const import CONF_ATTRACTIONS, DEFAULT_SCAN_INTERVAL, DOMAIN

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
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Manage ride selection options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        attractions = await async_fetch_attractions(self.hass)
        attraction_options = {
            attraction["wait_time_attraction_id"]: attraction["name"]
            for attraction in sorted(attractions, key=lambda item: item["name"].lower())
        }
        current = self.config_entry.options.get(CONF_ATTRACTIONS, [])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ATTRACTIONS, default=current): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=attraction_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        ),
                    ),
                }
            ),
        )
