"""Constants for Universal Studios Hollywood wait times."""

DOMAIN = "ush_wait_times"

DEFAULT_SCAN_INTERVAL = 60

API_URL = (
    "https://assets.universalparks.com/ush/wait-time/wait-time-attraction-list.json"
)

CONF_SCAN_INTERVAL = "scan_interval"

ATTR_STATUS = "status"
ATTR_QUEUE_TYPE = "queue_type"
ATTR_DISPLAY_WAIT_TIME = "display_wait_time"
ATTR_LAND_ID = "land_id"
ATTR_VENUE_ID = "venue_id"
ATTR_MODIFIED_AT = "modified_at"
ATTR_ATTRACTION_ID = "wait_time_attraction_id"
ATTR_RESORT_AREA = "resort_area_code"
ATTR_HAS_SINGLE_RIDER = "has_single_rider"
