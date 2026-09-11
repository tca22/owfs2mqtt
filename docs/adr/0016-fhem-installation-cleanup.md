# ADR-0016: FHEM installation and configuration boundary

- Status: Accepted
- Date: 2026-09-07
- Scope: FHEM integration

## Decision

Keep the bridge MQTT payload FHEM-independent. FHEM-specific presentation is
limited to the supplied `docs/fhem-stateformat.cfg` notify.

The documented FHEM setup uses `MQTT_SERVER` simple autocreate and one bridge
device. Sensor devices are created from the bridge regexp; no per-sensor
manual definitions are required.

The bridge owns MQTT topics and availability semantics. FHEM owns display
formatting through `stateFormat`.

## Consequences

- Installation is reproducible without copying ad-hoc per-sensor commands.
- Manual `stateFormat` values remain possible and are not overwritten.
- MQTT remains usable by consumers other than FHEM.
