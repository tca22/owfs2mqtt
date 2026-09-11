# ADR-0010: Separate sensor state from availability

- **Status:** Accepted
- **Date:** 2026-08-28
- **Decision:** V3

## Context

The JSON MQTT state topic is consumed by FHEM `MQTT2_SERVER`. During testing,
`ow2mqtt` published the literal payload `offline` to the same `state` topic
between JSON state messages. FHEM's `autocreate=complex` can therefore see a
non-JSON payload when a topic is first discovered and create a generic
`readingList` instead of the desired `json2nameValue($EVENT)` processing.

This made FHEM autocreate behavior dependent on which payload arrived first.

## Decision

State and availability are separate MQTT concepts:

- `1-wire/<alias>/state` **always contains JSON** in JSON mode.
- `1-wire/<alias>/availability` contains `online` or `offline` for the
  individual sensor. It is deliberately **not retained**.
- `1-wire/bridge/availability` represents the availability of the `ow2mqtt`
  bridge itself.
- The bridge availability uses MQTT Last Will and Testament (LWT), with
  `offline` as the will payload and `online` published after a successful
  connection.
- Sensor availability is derived from the OWServer read/discovery result and
  is published after the state message. The retained JSON state is the
  restart/autocreate source of truth.
- A sensor read failure publishes a JSON state with `available: false` and an
  `offline` sensor-availability message. A subsequent successful read
  publishes JSON with `available: true` and `online`.

A single MQTT client connection cannot have a separate MQTT LWT for every
sensor. Therefore per-sensor availability is explicitly published, while the
single LWT represents bridge availability.

## Consequences

### Positive

- `state` has one stable payload type in JSON mode.
- FHEM `autocreate=complex` can deterministically see JSON on first discovery.
- Sensor availability and bridge availability are unambiguous.
- No periodic `offline` traffic is generated merely because the bridge is
  still running.
- The design remains independent of FHEM-specific behavior.

### Negative

- Each sensor adds one availability topic per polling cycle.
- Consumers must distinguish sensor availability from bridge availability.
- Sensor availability is an application-level signal, not an MQTT connection
  LWT.
- Availability is non-retained so a newly restarted FHEM instance cannot see
  an availability-only payload before the retained JSON state.

## Compatibility

The existing JSON state schema remains compatible; `available` remains part of
that JSON payload. Flat/legacy mode keeps its existing per-field publishing
behavior, with the new availability topic added independently.
