# owfs2mqtt V3 1.0.0 release readiness

Status: **ready for public GitHub publication**

## Validated

- Python test suite: **15/15 passed**
- MQTT JSON/availability behavior covered by the existing test suite
- Dynamic discovery and removal handling covered by the existing test suite
- DS18B20, DS18S20, DS1822, DS2438, DS2401, DS1420 and DS2413 support present
- FHEM simple JSON autocreate documented
- Docker log rotation configured
- Deployment-specific MQTT host is no longer embedded in the public Compose file
- Host-side alias file defaults to `./owalias.txt`
- Site-specific private IP addresses and local `/mnt/docker/...` paths removed from the public tree
- Generated Python and pytest cache files removed from the release tree
- `.gitignore`, `.dockerignore`, GitHub Actions CI, issue template, PR template, `SECURITY.md`, and `CONTRIBUTING.md` included

## Deployment note

The public Compose file intentionally requires `MQTT_HOST`:

```bash
export MQTT_HOST=<your-mqtt-broker-host-or-ip>
export OWALIAS_FILE_HOST=./owalias.txt
docker compose up -d --build
```

Do not commit a real `owalias.txt`, `.env`, credentials, or local deployment overrides.

## Publication

Publish the repository at version `1.0.0` and create the annotated Git tag `v1.0.0`. See `GITHUB_RELEASE.md` for the exact commands.
