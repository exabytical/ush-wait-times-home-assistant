"""API helpers for Universal Studios Hollywood wait times."""

from __future__ import annotations

from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_URL


async def async_fetch_attractions(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Fetch the current attraction list from Universal Parks."""
    session = async_get_clientsession(hass)
    async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=20)) as response:
        response.raise_for_status()
        payload = await response.json(content_type=None)

    if not isinstance(payload, list):
        msg = "Unexpected API response format"
        raise TypeError(msg)

    return payload
