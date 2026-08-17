"""Basic tests for USH wait times integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL

from custom_components.ush_wait_times.const import DEFAULT_SCAN_INTERVAL, DOMAIN
from custom_components.ush_wait_times.sensor import (
    build_attraction_attributes,
    build_device_info,
    filter_selected_attractions,
    land_display_name,
    normalize_selected_ids,
    parse_sensor_state,
    parse_wait_time,
    slugify_attraction_id,
    standby_queue,
)


def test_domain():
    assert DOMAIN == "ush_wait_times"


def test_default_scan_interval():
    assert DEFAULT_SCAN_INTERVAL == 60


def test_manifest_path():
    import json
    from pathlib import Path

    manifest = json.loads(
        Path("custom_components/ush_wait_times/manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["domain"] == DOMAIN
    assert manifest["config_flow"] is True
    assert CONF_SCAN_INTERVAL or True


def test_slugify_attraction_id():
    attraction_id = "ush.upper.lot.rides.mario_kart_bowsers_challenge"
    assert slugify_attraction_id(attraction_id) == "upper_lot_rides_mario_kart_bowsers_challenge"


def test_standby_queue_prefers_standby():
    attraction = {
        "queues": [
            {"queue_type": "SINGLE", "display_wait_time": 10},
            {"queue_type": "STANDBY", "display_wait_time": 45},
        ]
    }
    assert standby_queue(attraction) == {"queue_type": "STANDBY", "display_wait_time": 45}


def test_parse_sensor_state():
    assert parse_sensor_state({"display_wait_time": "30", "status": "OPEN"}) == 30
    assert parse_sensor_state({"display_wait_time": 20, "status": "CLOSED"}) == "CLOSED"
    assert parse_sensor_state({"display_wait_time": None, "status": "CLOSED"}) == "CLOSED"
    assert parse_sensor_state({"display_wait_time": None, "status": "OPEN"}) is None
    assert parse_sensor_state(None) is None


def test_parse_wait_time():
    assert parse_wait_time({"display_wait_time": "30", "status": "OPEN"}) == 30
    assert parse_wait_time({"display_wait_time": 20, "status": "CLOSED"}) is None
    assert parse_wait_time(None) is None


def test_normalize_selected_ids():
    assert normalize_selected_ids([" a ", "b"]) == ["a", "b"]
    assert normalize_selected_ids("bad") == []
    assert normalize_selected_ids([]) == []


def test_land_display_name():
    assert land_display_name("ush.upper_lot.wwohp") == "Wizarding World"
    assert land_display_name("ush.upper_lot.super_nintendo_world") == "Super Nintendo World"


def test_filter_selected_attractions():
    attractions = [
        {
            "wait_time_attraction_id": "ush.upper_lot.rides.mario_kart_bowsers_challenge",
            "name": "Mario Kart",
        },
        {
            "wait_time_attraction_id": "ush.lower_lot.rides.jurassic_world_the_ride",
            "name": "Jurassic World",
        },
    ]
    selected = filter_selected_attractions(
        attractions,
        ["ush.upper_lot.rides.mario_kart_bowsers_challenge"],
    )
    assert len(selected) == 1
    assert selected[0]["name"] == "Mario Kart"
    assert filter_selected_attractions(attractions, []) == []


def test_build_attraction_attributes():
    attraction = {
        "wait_time_attraction_id": "ush.upper_lot.rides.mario_kart_bowsers_challenge",
        "land_id": "ush.upper_lot.super_nintendo_world",
        "venue_id": "ush.upper_lot",
        "resort_area_code": "USH",
        "modified_at": "2026-08-16T17:32:07.960Z",
        "has_single_rider": False,
        "name": "Mario Kart",
        "category": "general",
    }
    queue = {"queue_type": "STANDBY", "status": "OPEN", "display_wait_time": 45}
    attrs = build_attraction_attributes(attraction, queue)
    assert attrs["status"] == "OPEN"
    assert attrs["display_wait_time"] == 45
    assert attrs["land"] == "Super Nintendo World"
    assert attrs["name"] == "Mario Kart"


def test_build_device_info():
    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="USH Wait Times",
        data={},
        source="user",
        entry_id="test-entry-id",
        unique_id=DOMAIN,
    )
    device_info = build_device_info(entry)
    assert device_info["identifiers"] == {(DOMAIN, "test-entry-id")}
    assert device_info["name"] == "USH Wait Times"
