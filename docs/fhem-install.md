# FHEM installation

## Prerequisites

- FHEM `MQTT_SERVER` is connected to the MQTT broker.
- Leave `autocreate` on `MQTT_SERVER` unset (simple autocreate).
- The bridge is publishing JSON mode under `1-wire`.

## Bridge device

Create the bridge device once:

```text
define ow2mqtt_bridge MQTT2_DEVICE ow2mqtt
attr ow2mqtt_bridge IODev MQTT_SERVER
attr ow2mqtt_bridge autocreate 1
attr ow2mqtt_bridge bridgeRegexp 1-wire/(?!bridge/)([A-Za-z0-9._-]+)/(state|availability):.* "owfs_$1"
attr ow2mqtt_bridge stateFormat availability
```

The regexp maps both sensor `state` and sensor `availability` topics to the
same `owfs_*` device and deliberately excludes `1-wire/bridge/availability`.

## Automatic STATE formatting

Load `docs/fhem-stateformat.cfg` once:

```text
include docs/fhem-stateformat.cfg
```

The notify maps:

| Device | FHEM STATE |
|---|---|
| DS18B20 / DS18S20 / DS1822 | temperature, 1 decimal + `°C` |
| DS2438 with alias `pressure` | pressure in `bar` |
| Other DS2438 | `VDD` in `V` |
| DS2413 | `A: PIO_A | B: PIO_B` |
| DS2401 / DS1420 | `available` |

Only devices without an explicit `stateFormat` are changed.

## Expected result

With JSON autocreate, sensor readings are created directly from the JSON
payload. A missing sensor is retained as an FHEM device and receives
`available=false`; when it returns, `available=true` is published again.
The MQTT payload is not modified for FHEM presentation.
