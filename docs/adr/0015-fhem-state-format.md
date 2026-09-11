# ADR-0015: Automatic FHEM STATE formatting

- Status: Accepted
- Date: 2026-09-04
- Scope: FHEM integration

## Context

Automatically created `MQTT2_DEVICE` sensor devices receive the JSON
readings correctly, but without a `stateFormat` FHEM displays `STATE=???`.
The MQTT payload itself should remain neutral and must not be changed solely
to satisfy FHEM presentation.

## Decision

Provide a small FHEM-side `notify` definition. It watches the `device_type`
reading of `owfs_*` devices and assigns a `stateFormat` only if none is
already configured.

The initial mapping is:

- DS18B20 / DS18S20 / DS1822 → temperature with 1 decimal place and `°C`
- DS2438 with alias `pressure` → `pressure bar`
- other DS2438 → `VDD V`
- DS2413 → `A: PIO_A | B: PIO_B`
- DS2401 / DS1420 → `available`


## Consequences

- MQTT/JSON remains unchanged and FHEM-independent.
- One FHEM definition handles both existing and future autocreated devices.
- Explicit per-device `stateFormat` values are not overwritten.
- The presentation logic is easy to extend later without changing the bridge.
