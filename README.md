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

1. **Settings → Devices & Services → Add Integration** → **Universal Studios Hollywood Wait Times**
2. Set the poll interval (optional)
3. Open the integration → **Configure** → select the rides you want to track

No sensors are created until you pick rides in **Configure**. All selected rides appear under one device: **Universal Studios Hollywood**.

## Entities

Each selected ride becomes its own sensor. State is wait time in minutes, or `CLOSED` when the ride is not operating.

Examples:

- `sensor.ush_upper_lot_rides_mario_kart_bowsers_challenge`
- `sensor.ush_upper_lot_rides_harry_potter_and_the_forbidden_journey`
- `sensor.ush_lower_lot_rides_jurassic_world_the_ride`

Each sensor also exposes attributes such as `status`, `land_id`, `venue_id`, and `modified_at`.

## Changing rides

**Settings → Devices & Services → Universal Studios Hollywood Wait Times → Configure**

Add or remove rides at any time. The integration reloads and updates sensors automatically.

## Upgrading from v1.1.x

1. Update via HACS and restart Home Assistant
2. Open **Configure** and select your rides
3. Delete the old `sensor.ush_wait_times` entity from the entity registry if it remains

## License

MIT
