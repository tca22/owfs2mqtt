# owfs2mqtt

**OWFS/OWServer → MQTT bridge for 1-Wire devices**

Version: `1.0.0`

The project reads 1-Wire devices through the native OWServer protocol on TCP/4304 and publishes their values to MQTT. Discovery is based on devices exposed by OWServer; `owalias.txt` is used only to map ROM IDs to human-readable aliases. It does not scrape the OWFS HTTP interface.

## Current scope

- Native OWServer protocol via `pyownet`
- UTF-8 `owalias.txt`
- Dynamic discovery through OWServer; `owalias.txt` is optional for naming
- DS18S20 / DS1822 / DS18B20 temperature devices
- DS2438
- DS2401
- DS1420
- DS2413 read support (`PIO_A` / `PIO_B`)
- JSON MQTT state topics
- Separate per-sensor availability topics
- Removed sensors remain represented in FHEM and are marked unavailable
- Bridge availability via MQTT LWT and OWServer connectivity state
- Flat/legacy MQTT mode
- ROM ID, alias and family in every JSON state
- special:Pressure calculation for the configured DS2438 (attached to an industrial transducer)

## MQTT

Default client ID:

`ow2mqtt`

Default root topic:

`1-wire`

JSON example:

`1-wire/UG_Kesseltemperatur/state`

Availability:

`1-wire/UG_Kesseltemperatur/availability`

Bridge availability:

`1-wire/bridge/availability`

```json
{"alias":"UG_Kesseltemperatur","rom_id":"289435AF030000F2","family":"28","device_type":"DS18B20","available":true,"temperature":69.4375}
```

The state topic always contains JSON in JSON mode; `offline` is never published to a state topic. A sensor that disappears from a successful OWServer discovery is not deleted; its availability is published as `offline` so FHEM keeps the device and marks it unavailable. Sensor availability is published separately as `online` or `offline` after the state message and is not retained. The bridge itself uses MQTT Last Will and Testament on retained `1-wire/bridge/availability`.

Flat mode:

```text
1-wire/UG_Kesseltemperatur/temperature
```

Select with:

```text
MQTT_MODE=json
```

or:

```text
MQTT_MODE=flat
```

## FHEM

The intended consumer is FHEM's `MQTT_SERVER`. JSON mode minimizes MQTT traffic and groups one sensor's state into one message. Flat mode is provided for installations where direct FHEM readings are preferred.

### Automatic FHEM STATE formatting

The MQTT payload remains FHEM-independent. To give automatically created
`owfs_*` devices a useful `STATE`, add the supplied
`docs/fhem-stateformat.cfg` once to the FHEM configuration.

It installs one `notify` which reacts to the `device_type` reading and sets
`stateFormat` only when no explicit `stateFormat` is already configured:

- DS18B20 / DS18S20 / DS1822 → temperature with 1 decimal place and `°C`
- DS2438 with alias `pressure` → `pressure bar`
- other DS2438 → `VDD V`
- DS2413 → `A: PIO_A | B: PIO_B`
- DS2401 / DS1420 → `available`

Existing devices receive the setting with their next `device_type` event; new
devices are handled automatically after autocreate. Manually configured
`stateFormat` values are not overwritten.

For the FHEM bridge device `ow2mqtt_bridge` (CID/DEF `ow2mqtt`), the V3
bridge mapping should match both state and sensor availability, but not the
bridge's own availability topic:

```text
attr ow2mqtt_bridge autocreate 1
attr ow2mqtt_bridge bridgeRegexp 1-wire/(?!bridge/)([A-Za-z0-9._-]+)/(state|availability):.* "owfs_$1"
```

For OW2MQTT, leave the `autocreate` attribute on `MQTT2_SERVER` unset so FHEM uses its default/simple mode. The generated `owfs_<alias>` device should then use `json2nameValue($EVENT)` without the `state_` prefix. `autocreate=complex` is intentionally not used here because it generates a topic-derived prefix such as `state_temperature`. The availability topic follows the state and is non-retained, avoiding an availability-only first message during FHEM restart.

## Important dependency note

`pyownet` implements the OWServer protocol and is used as an external dependency. Its latest PyPI release is old, so Python-version compatibility should be verified when changing the base Python image or dependency set.

## Development

```bash
python -m pytest
```

For DS2413 software integration, OWServer can be run with the fake adapter (`--fake=3A`) on a separate test port; see `docs/test-ds2413-fake.md`.

The real OWServer should be tested with:

```bash
owdir -s <host>:4304 /
owread -s <host>:4304 /<alias>/temperature
```

before deploying the bridge.

## License

The project code is intended to be released under GNU Affero General Public License v3.0.


## Release 1.0.0

Version 1.0.0 is the validated V3 release. It includes Docker log rotation, deployment hardening, dynamic discovery, sensor availability handling, and the FHEM integration documented below.

## Deployment with the existing OWFS container

The bridge must be attached to the same Docker network as the existing
`owfs` container so that `owfs:4304` resolves. The bridge does not need
USB access, `privileged: true`, or `/dev/bus/usb`.

The Compose file provides environment-variable overrides for deployment-specific
settings. Public repository defaults are intentionally generic; set deployment-specific
values in the environment before starting the container. In particular:

```text
OW_SERVER_HOST
OW_SERVER_PORT
MQTT_HOST
MQTT_PORT
MQTT_CLIENT_ID
MQTT_ROOT_TOPIC
MQTT_MODE
POLL_INTERVAL
LOG_LEVEL
OWALIAS_FILE_HOST
```

`config/config.yaml` is included in the image as the baseline configuration;
environment variables take precedence. `MQTT_HOST` is required by the public
Compose file. The host-side `owalias.txt` path defaults to `./owalias.txt` and can
be changed with `OWALIAS_FILE_HOST` without editing the Compose file.

For example, before starting the bridge, set the MQTT broker host explicitly:

```bash
export MQTT_HOST=<your-mqtt-broker-host-or-ip>
export OWALIAS_FILE_HOST=./owalias.txt
docker compose up -d --build
```

The Docker container uses the `json-file` logging driver with log rotation:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

This limits retained container logs to approximately 30 MB (three rotated
files of up to 10 MB each). This setting applies to Docker's container logs;
it does not change the application's log level or MQTT behavior.

The supplied compose file intentionally does not recreate the existing
OWFS container. Verify the connection before deployment with:

```text
owdir -s owfs:4304 /
owread -s owfs:4304 /UG_Kesseltemperatur/temperature
```


## FHEM installation

The bridge itself requires no FHEM-specific configuration beyond the MQTT
connection. For the intended simple JSON autocreate setup:

1. Keep `autocreate` on `MQTT_SERVER` unset.
2. Define the bridge device with `autocreate 1` and the V3 `bridgeRegexp`.
3. Load `docs/fhem-stateformat.cfg` once. It creates the
   `owfs2mqtt_stateFormat` notify.
4. Restart the bridge or wait for the next sensor update. FHEM creates
   `owfs_<alias>` devices automatically.
5. If an alias is missing, the ROM ID is used in the device name.

The supplied state-format notify only adds `stateFormat` when a device has no
explicit value. Existing manual formatting therefore remains authoritative.

Example bridge definition:

```text
define ow2mqtt_bridge MQTT2_DEVICE ow2mqtt
attr ow2mqtt_bridge IODev MQTT_SERVER
attr ow2mqtt_bridge autocreate 1
attr ow2mqtt_bridge bridgeRegexp 1-wire/(?!bridge/)([A-Za-z0-9._-]+)/(state|availability):.* "owfs_$1"
attr ow2mqtt_bridge stateFormat availability
```

Then load:

```text
include docs/fhem-stateformat.cfg
```

`owfs_*` sensor devices are expected to contain the JSON readings directly
(`temperature`, `VDD`, `pressure`, `PIO_A`, `PIO_B`, `available`, etc.).
`stateFormat` affects only the displayed FHEM `STATE`, not the MQTT payload.

## Repository

The public repository contains the application source, tests, documentation,
Docker deployment files, and an example alias file.

Do not commit the site-specific `owalias.txt`, credentials, `.env` files, or
local deployment overrides. Use `owalias.example.txt` as the template for an
alias mapping.

### Tests

Run:

```bash
pytest -q
```

The V3 release was validated with 15 automated tests plus end-to-end deployment
testing on the target Photon (docker).

