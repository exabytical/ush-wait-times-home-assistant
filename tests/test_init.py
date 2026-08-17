"""Basic tests for USH wait times integration."""

from homeassistant.const import CONF_SCAN_INTERVAL

from custom_components.ush_wait_times.const import DEFAULT_SCAN_INTERVAL, DOMAIN
from custom_components.ush_wait_times.sensor import (
    build_wait_time_attributes,
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
    attraction_id = "ush.upper_lot.rides.mario_kart_bowsers_challenge"
    assert slugify_attraction_id(attraction_id) == "upper_lot_rides_mario_kart_bowsers_challenge"


def test_standby_queue_prefers_standby():
    attraction = {
        "queues": [
            {"queue_type": "SINGLE", "display_wait_time": 10},
            {"queue_type": "STANDBY", "display_wait_time": 45},
        ]
    }
    assert standby_queue(attraction) == {"queue_type": "STANDBY", "display_wait_time": 45}


def test_parse_wait_time():
    assert parse_wait_time({"display_wait_time": "30"}) == 30
    assert parse_wait_time({"display_wait_time": None}) is None
    assert parse_wait_time(None) is None


def test_build_wait_time_attributes():
    attractions = [
        {
            "wait_time_attraction_id": "ush.upper_lot.rides.mario_kart_bowsers_challenge",
            "queues": [{"queue_type": "STANDBY", "display_wait_time": 45}],
        },
        {
            "wait_time_attraction_id": "ush.lower_lot.rides.jurassic_world_the_ride",
            "queues": [{"queue_type": "STANDBY", "display_wait_time": 30}],
        },
    ]
    attrs = build_wait_time_attributes(attractions)
    assert attrs == {
        "ush_upper_lot_rides_mario_kart_bowsers_challenge": 45,
        "ush_lower_lot_rides_jurassic_world_the_ride": 30,
    }
