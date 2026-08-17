"""DataUpdateCoordinator for USH wait times."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class UshWaitTimeCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Fetch wait times for all attractions."""

    def __init__(self, hass: HomeAssistant, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Universal Studios Hollywood Wait Times",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._session = aiohttp.ClientSession()

    async def async_shutdown(self) -> None:
        await self._session.close()

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            async with self._session.get(API_URL, timeout=aiohttp.ClientTimeout(total=20)) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error fetching wait times: {err}") from err

        if not isinstance(payload, list):
            raise UpdateFailed("Unexpected API response format")

        return payload
