# Universal Studios Hollywood Wait Times

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant custom integration for live **Universal Studios Hollywood** attraction wait times.

![icon](images/icon.png)

Same repository layout as [gickowtf/pixoo-homeassistant](https://github.com/gickowtf/pixoo-homeassistant).

## Install

### HACS

1. HACS → Settings → Custom repositories → add [this repo](https://github.com/exabytical/ush-wait-times-home-assistant) as **Integration**
2. Install **Universal Studios Hollywood Wait Times**
3. Restart Home Assistant

### Manual

Copy `custom_components/ush_wait_times` to HA `config/custom_components/` and restart.

## Setup

**Settings → Devices & Services → Add Integration** → **Universal Studios Hollywood Wait Times**

## Entity

The integration creates a single sensor:

- `sensor.ush_wait_times`

The sensor state is `unknown` — all wait times live in **attributes**, keyed by attraction slug:

```yaml
{{ state_attr('sensor.ush_wait_times', 'ush_upper_lot_rides_mario_kart_bowsers_challenge') }}
{{ state_attr('sensor.ush_wait_times', 'ush_upper_lot_rides_harry_potter_and_the_forbidden_journey') }}
{{ state_attr('sensor.ush_wait_times', 'ush_lower_lot_rides_jurassic_world_the_ride') }}
```

Each attribute value is the standby wait time in minutes (or `null` if unavailable).

No devices or areas are created.

## Upgrading from v1.0.x

If you previously installed v1.0.x (which created one sensor per attraction):

1. Remove the integration (Settings → Devices & Services → Universal Studios Hollywood Wait Times → Delete).
2. Delete any leftover per-ride devices, sensors, and theme-park Areas.
3. Re-add the integration — you should see exactly one entity: `sensor.ush_wait_times`.

## License

MIT
