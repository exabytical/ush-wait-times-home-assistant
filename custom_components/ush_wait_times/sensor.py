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

LAND_SORT_ORDER = {
    "ush.upper_lot.super_nintendo_world": 0,
    "ush.lower_lot.super_nintendo_world": 1,
    "ush.upper_lot.wwohp": 2,
    "ush.upper_lot": 3,
    "ush.lower_lot": 4,
}


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
    """Return wait minutes, using 0 when the ride is closed without a posted wait."""
    if queue is None:
        return None

    wait = queue.get("display_wait_time")
    if wait is not None:
        try:
            return int(float(wait))
        except (TypeError, ValueError):
            pass

    status = (queue.get("status") or "").upper()
    if status in {"CLOSED", "OFFLINE"}:
        return 0

    return None


def normalize_selected_ids(selected_ids: Any) -> list[str]:
    """Normalize stored option values into a list of attraction IDs."""
    if not selected_ids:
        return []
    if not isinstance(selected_ids, list):
        return []
    return [item.strip() for item in selected_ids if isinstance(item, str) and item.strip()]


def filter_selected_attractions(
    attractions: list[dict[str, Any]], selected_ids: list[str]
) -> list[dict[str, Any]]:
    """Return selected attractions in land/name order."""
    normalized = normalize_selected_ids(selected_ids)
    if not normalized:
        return []

    selected = set(normalized)
    filtered = [
        attraction
        for attraction in attractions
        if attraction.get("wait_time_attraction_id") in selected
    ]
    return sorted(
        filtered,
        key=lambda attraction: (
            LAND_SORT_ORDER.get(attraction.get("land_id", ""), 99),
            (attraction.get("name") or "").lower(),
        ),
    )


def land_display_name(land_id: str | None) -> str:
    """Return a readable land name for grouping."""
    if not land_id:
        return "Universal Studios Hollywood"

    labels = {
        "ush.upper_lot.super_nintendo_world": "Super Nintendo World",
        "ush.lower_lot.super_nintendo_world": "Super Nintendo World",
        "ush.upper_lot.wwohp": "Wizarding World",
        "ush.upper_lot": "Upper Lot",
        "ush.lower_lot": "Lower Lot",
    }
    if land_id in labels:
        return labels[land_id]

    return land_id.split(".")[-1].replace("_", " ").title()


def build_device_info(entry: ConfigEntry) -> DeviceInfo:
    """Return shared device info for all ride sensors."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="USH Wait Times",
        manufacturer="Universal Parks",
        model="Attraction Wait Times",
    )


def build_attraction_attributes(
    attraction: dict[str, Any], queue: dict[str, Any] | None
) -> dict[str, Any]:
    """Build extra state attributes for a single attraction."""
    queue = queue or {}
    land_id = attraction.get("land_id")
    return {
        ATTR_ATTRACTION_ID: attraction.get("wait_time_attraction_id"),
        ATTR_STATUS: queue.get("status"),
        ATTR_QUEUE_TYPE: queue.get("queue_type"),
        ATTR_DISPLAY_WAIT_TIME: queue.get("display_wait_time"),
        ATTR_LAND_ID: land_id,
        "land": land_display_name(land_id),
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
    _attr_suggested_display_precision = 0

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
