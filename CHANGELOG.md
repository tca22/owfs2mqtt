# Changelog

## M10.2 – Public release readiness

- Finalized the GitHub publication checklist and release documentation for V3 1.0.0.
- Updated README release wording from release-candidate/alpha language to the 1.0.0 release.
- Removed generated Python and pytest cache artifacts from the public release tree.
- Re-verified public-repository hygiene and the 15-test suite.

## M10.1 – Public repository hygiene

- Removed site-specific host paths and private network defaults from the public repository configuration.
- Made `MQTT_HOST` explicit in Docker Compose instead of embedding a deployment-specific IP address.
- Changed the default host-side alias file path to `./owalias.txt`.
- Kept the runtime MQTT/OWServer behavior unchanged.


## 1.0.0-rc2

- Release candidate after completed V3 end-to-end and deployment acceptance.
- Includes Docker `json-file` log rotation and the validated M7 deployment hardening.
- No MQTT topic, payload, discovery, availability, or sensor behavior changes.

## 0.1.0-alpha-m7.4

- Added Docker `json-file` log rotation with `max-size=10m` and `max-file=3`.
- Limits retained container logs to approximately 30 MB.
- No change to MQTT, discovery, availability, or sensor payload behavior.

## 0.1.0-alpha-m7.2

- Hardened deployment configuration with environment-variable overrides in Compose.
- Baked the default YAML configuration into the image while keeping deployment-specific values overridable through the environment.
- Parameterized the host-side alias-file path via `OWALIAS_FILE_HOST`.
- Added DS1420 (`family 81`) to the unavailable-sensor device-type mapping.
- No change to MQTT topic or JSON payload semantics.

## 0.1.0-alpha-m7.1

- Release-hygiene cleanup after M6.3 end-to-end acceptance.
- Updated project/version reporting from M6.1 to M7.1.
- Removed generated Python and pytest cache files from the release tree.
- Corrected FHEM test documentation to reference `MQTT_SERVER` simple autocreate.
- Kept the validated FHEM bridge and state-format configuration unchanged.
- No MQTT payload, discovery, availability, or sensor behavior changes.
