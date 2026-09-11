# ADR-0011: FHEM autocreate uses the simple mode for OW2MQTT JSON state topics

## Status
Accepted

## Context

OW2MQTT publishes each sensor state on `1-wire/<alias>/state` as a JSON payload. FHEM's `MQTT2_SERVER` can create MQTT2_DEVICE instances automatically. During testing, `autocreate=complex` generated readingList entries such as:

```text
1-wire/UG_Kesseltemperatur/state:.* { json2nameValue($EVENT, 'state_', $JSONMAP) }
```

This intentionally adds the topic name (`state_`) as a prefix to generated reading names, resulting in readings such as `state_temperature` and `state_rom_id`.

For OW2MQTT this prefix is not required because each sensor has its own MQTT2_DEVICE and its state topic is dedicated to that device. FHEM's documentation recommends the default/simple autocreate mode for known, simple JSON devices and documents the `STATE_` prefix as a characteristic of the complex mode.

## Decision

OW2MQTT's FHEM integration targets **simple autocreate**, not `autocreate=complex`.

The MQTT2_SERVER `autocreate` attribute should therefore normally be left unset (FHEM's default/simple behavior). The OW2MQTT bridge device keeps `autocreate 1` and its `bridgeRegexp` for creating one `owfs_<alias>` device per sensor.

The desired generated readingList is:

```text
1-wire/<alias>/state:.* { json2nameValue($EVENT) }
```

so JSON fields become direct readings such as `temperature`, `rom_id`, `family`, `device_type` and `available`.

## Consequences

- No unwanted `state_` prefix on per-sensor readings.
- One sensor has one dedicated MQTT2_DEVICE, so topic-origin prefixes are unnecessary.
- `autocreate=complex` remains useful for other FHEM integrations, but is not required for OW2MQTT.
- The first state message must remain JSON; therefore the V3 separation of `state` and `availability` remains important.
