# ADR-0013: Dynamic OWFS discovery without mandatory aliases

- Status: Accepted
- Date: 2026-08-30
- Scope: OWFS/OWServer → MQTT V3

## Context

V3 discovery previously depended on entries in `owalias.txt`. This prevented an OWFS device from being published when it was present on the 1-Wire bus but had no configured alias. The DS2413 fake-adapter test demonstrated the issue: OWServer exposed `/3A.67C6697351FF`, but the bridge continued to report only the configured sensors.

The alias file is useful for stable, human-readable MQTT/FHEM names, but it should not be the device-discovery mechanism itself.

## Decision

OW2MQTT performs discovery directly from the OWServer root directory.

For each candidate OWFS device entry, the bridge reads its `address` property and uses the resulting canonical 16-character ROM ID as the device identity. `owalias.txt` is optional and is used only to replace the ROM ID with a configured alias.

Configured aliases that are currently absent remain represented as unavailable sensors, preserving the existing availability behaviour.

Non-device OWFS entries such as `bus.0`, `settings`, `system`, etc. are ignored.

## Consequences

- Newly connected/unknown 1-Wire devices can be discovered without editing `owalias.txt`.
- `owalias.txt` remains useful for readable and stable names.
- The DS2413 fake adapter can be tested without adding a temporary alias.
- A canonical ROM address must be obtainable from OWFS for a dynamically discovered device.
- The MQTT/FHEM integration remains independent of the alias file.
