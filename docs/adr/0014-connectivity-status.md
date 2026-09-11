# ADR-0014 – Connectivity status and outage handling

## Status

Accepted

## Context

OWServer and MQTT failures must not terminate `owfs2mqtt`. The M5.2
failure tests showed that the process already recovers automatically after
both services return, but FHEM could not distinguish an infrastructure
outage from a healthy bridge: the bridge availability remained `online` and
sensor `available` readings remained `true`.

## Decision

The bridge availability topic has two layers:

- MQTT transport availability remains represented by MQTT LWT.
- Application availability additionally reflects OWServer reachability.

When an OWServer cycle fails, `1-wire/bridge/availability` is published as
retained `offline` when MQTT is available, and all last-known sensors are
published with `available=false`.

When OWServer becomes reachable again, the bridge availability is published
as retained `online` before normal sensor states are published.

When MQTT publishing itself fails, the bridge does not attempt a second
`unavailable` publish for the same sensor. MQTT LWT remains responsible for
broker-visible transport availability. Paho's automatic reconnect is
preserved, and on reconnect the retained application `online` state is
re-published when OWServer is still known to be healthy.

## Consequences

- FHEM can observe OWServer outages through bridge and sensor availability.
- MQTT outages do not cause a cascade of redundant publish failures.
- The last discovered sensor list is retained in memory for OWServer outage
  reporting.
- No new reconnect mechanism is introduced; M5.2 already demonstrated that
  recovery works in the deployed environment.
