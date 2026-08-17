"""Sensor platform for Universal Studios Hollywood wait times."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import UshWaitTimeCoordinator


def slugify_attraction_id(attraction_id: str) -> str:
    slug = attraction_id.replace("ush.", "").replace(".", "_")
    slug = re.sub(r"[^a-z0-9_]+", "_", slug.lower()).strip("_")
    return slug


def standby_queue(attraction: dict[str, Any]) -> dict[str, Any] | None:
    for queue in attraction.get("queues", []):
        if queue.get("queue_type") == "STANDBY":
            return queue
    queues = attraction.get("queues", [])
    return queues[0] if queues else None


def parse_wait_time(queue: dict[str, Any] | None) -> int | None:
    if queue is None:
        return None
    wait = queue.get("display_wait_time")
    if wait is None:
        return None
    try:
        return int(wait)
    except (TypeError, ValueError):
        return None


def build_wait_time_attributes(attractions: list[dict[str, Any]]) -> dict[str, Any]:
    """Build flat attribute dict keyed by attraction slug."""
    attrs: dict[str, Any] = {}
    for attraction in attractions:
        attraction_id = attraction.get("wait_time_attraction_id")
        if not attraction_id:
            continue
        slug = f"ush_{slugify_attraction_id(attraction_id)}"
        attrs[slug] = parse_wait_time(standby_queue(attraction))
    return attrs


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: UshWaitTimeCoordinator = entry.runtime_data
    async_add_entities([UshWaitTimesSensor(coordinator, entry)])


class UshWaitTimesSensor(CoordinatorEntity[UshWaitTimeCoordinator], SensorEntity):
    """All USH attraction wait times in a single sensor."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:timer-sand"
    _attr_name = "USH Wait Times"

    def __init__(self, coordinator: UshWaitTimeCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = entry.entry_id
        self._attr_suggested_object_id = "ush_wait_times"

    @property
    def native_value(self) -> None:
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = build_wait_time_attributes(self.coordinator.data or [])
        if self.coordinator.last_update_success and self.coordinator.last_update_success_time:
            attrs["last_updated"] = self.coordinator.last_update_success_time.isoformat()
        return attrs
