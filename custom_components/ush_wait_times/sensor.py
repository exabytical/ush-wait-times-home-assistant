"""Sensor platform for Universal Studios Hollywood wait times."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ATTRACTION_ID,
    ATTR_DISPLAY_WAIT_TIME,
    ATTR_HAS_SINGLE_RIDER,
    ATTR_LAND_ID,
    ATTR_MODIFIED_AT,
    ATTR_QUEUE_TYPE,
    ATTR_RESORT_AREA,
    ATTR_STATUS,
    ATTR_VENUE_ID,
    CONF_ATTRACTIONS,
    DOMAIN,
)
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


def filter_selected_attractions(
    attractions: list[dict[str, Any]], selected_ids: list[str]
) -> list[dict[str, Any]]:
    """Return attractions whose IDs are in the selected list."""
    if not selected_ids:
        return []
    selected = set(selected_ids)
    return [
        attraction
        for attraction in attractions
        if attraction.get("wait_time_attraction_id") in selected
    ]


def build_device_info(entry: ConfigEntry) -> DeviceInfo:
    """Return shared device info for all ride sensors."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Universal Studios Hollywood",
        manufacturer="Universal Parks",
        model="Wait Times",
    )


def build_attraction_attributes(
    attraction: dict[str, Any], queue: dict[str, Any] | None
) -> dict[str, Any]:
    """Build extra state attributes for a single attraction."""
    queue = queue or {}
    return {
        ATTR_ATTRACTION_ID: attraction.get("wait_time_attraction_id"),
        ATTR_STATUS: queue.get("status"),
        ATTR_QUEUE_TYPE: queue.get("queue_type"),
        ATTR_DISPLAY_WAIT_TIME: queue.get("display_wait_time"),
        ATTR_LAND_ID: attraction.get("land_id"),
        ATTR_VENUE_ID: attraction.get("venue_id"),
        ATTR_RESORT_AREA: attraction.get("resort_area_code"),
        ATTR_MODIFIED_AT: attraction.get("modified_at"),
        ATTR_HAS_SINGLE_RIDER: attraction.get("has_single_rider"),
        "name": attraction.get("name"),
        "category": attraction.get("category"),
    }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: UshWaitTimeCoordinator = entry.runtime_data
    selected_ids = entry.options.get(CONF_ATTRACTIONS, [])
    attractions = filter_selected_attractions(coordinator.data or [], selected_ids)
    async_add_entities(
        UshWaitTimeSensor(coordinator, entry, attraction) for attraction in attractions
    )


class UshWaitTimeSensor(CoordinatorEntity[UshWaitTimeCoordinator], SensorEntity):
    """Wait time for a selected USH attraction."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:timer-sand"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(
        self,
        coordinator: UshWaitTimeCoordinator,
        entry: ConfigEntry,
        attraction: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attraction_id = attraction["wait_time_attraction_id"]
        self._attr_unique_id = self._attraction_id
        self._attr_suggested_object_id = f"ush_{slugify_attraction_id(self._attraction_id)}"
        self._attr_name = attraction["name"]
        self._attr_device_info = build_device_info(entry)

    @property
    def available(self) -> bool:
        return super().available and self._attraction is not None

    @property
    def _attraction(self) -> dict[str, Any] | None:
        for attraction in self.coordinator.data or []:
            if attraction.get("wait_time_attraction_id") == self._attraction_id:
                return attraction
        return None

    @property
    def native_value(self) -> int | None:
        attraction = self._attraction
        if attraction is None:
            return None
        return parse_wait_time(standby_queue(attraction))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attraction = self._attraction
        if attraction is None:
            return {}
        return build_attraction_attributes(attraction, standby_queue(attraction))
