import logging
import os
import time

from .config import load_config
from .discovery import load_aliases, discover, find_removed_sensors
from .owserver import OWServerClient
from .sensors import read_sensor
from .mqtt import MQTTPublisher, MQTTConnectionError

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("ow2mqtt")


def main():
    config = load_config(os.getenv("CONFIG_FILE", "/config/config.yaml"))
    aliases = load_aliases(config.alias_file)

    log.info("ow2mqtt %s starting", "1.0.0-rc2")
    log.info("OWServer: %s:%s", config.ow_host, config.ow_port)
    log.info(
        "MQTT: %s:%s client_id=%s root=%s mode=%s",
        config.mqtt_host,
        config.mqtt_port,
        config.mqtt_client_id,
        config.mqtt_root_topic,
        config.mqtt_mode,
    )

    ow = OWServerClient(config.ow_host, config.ow_port, config.ow_timeout)
    mqtt = MQTTPublisher(config)
    mqtt.connect()

    # Keep sensors whose state has been successfully announced via MQTT.
    # This lets us distinguish a genuine device removal from an OWServer
    # outage, and lets a removal announcement be retried after an MQTT outage.
    known_sensors = {}
    ow_available = False

    try:
        while True:
            try:
                ow.connect()
                sensors = discover(ow, aliases)
                log.info("Discovered %d sensor(s)", len(sensors))

                removed = find_removed_sensors(known_sensors.values(), sensors)
                mqtt_cycle_failed = False
                for sensor in removed:
                    try:
                        mqtt.publish_sensor_unavailable(sensor)
                        known_sensors.pop(sensor.rom_id, None)
                        log.info("Sensor removed: %s", sensor.alias)
                    except MQTTConnectionError as exc:
                        # Keep the sensor in known_sensors so the removal is
                        # retried once MQTT connectivity returns. Do not treat
                        # this as an OWServer failure.
                        log.error("Failed to publish removal for %s: %s", sensor.alias, exc)
                        mqtt_cycle_failed = True
                        break
                    except Exception as exc:
                        log.error(
                            "Failed to publish removal for %s: %s",
                            sensor.alias,
                            exc,
                        )

                if mqtt_cycle_failed:
                    time.sleep(config.poll_interval)
                    continue

                if not ow_available:
                    try:
                        mqtt.set_backend_available(True)
                        ow_available = True
                    except Exception as exc:
                        # MQTT is unavailable; its LWT represents bridge
                        # availability. Do not treat this as an OWServer error.
                        log.error("Failed to publish bridge online state: %s", exc)
                        ow_available = False

                for sensor in sensors:
                    try:
                        data = read_sensor(ow, sensor, config)
                        mqtt.publish_sensor(data)
                        known_sensors[sensor.rom_id] = sensor
                        log.debug("Published %s", sensor.alias)
                    except Exception as exc:
                        log.error("Sensor failed: %s: %s", sensor.alias, exc)

                        # If MQTT itself failed, retrying with an unavailable
                        # message only produces the same error. For genuine
                        # sensor/read errors MQTT is still usable, so publish
                        # an explicit unavailable state.
                        if not isinstance(exc, MQTTConnectionError):
                            try:
                                mqtt.publish_sensor_unavailable(sensor)
                                known_sensors[sensor.rom_id] = sensor
                            except Exception as unavailable_exc:
                                log.error(
                                    "Failed to publish unavailable state: %s: %s",
                                    sensor.alias,
                                    unavailable_exc,
                                )

            except Exception as exc:
                log.error("OWServer cycle failed: %s", exc)

                # MQTT is normally still available here. Reflect the
                # OWServer outage on the retained bridge topic and mark the
                # last known sensors unavailable.
                if ow_available:
                    try:
                        mqtt.set_backend_available(False)
                    except Exception as mqtt_exc:
                        log.error(
                            "Failed to publish bridge offline state: %s",
                            mqtt_exc,
                        )
                    ow_available = False

                for sensor in known_sensors.values():
                    try:
                        mqtt.publish_sensor_unavailable(sensor)
                    except Exception as mqtt_exc:
                        # Once MQTT fails, further retries in this cycle are
                        # pointless. The broker LWT handles bridge availability.
                        log.error(
                            "Unable to publish unavailable state for %s: %s",
                            sensor.alias,
                            mqtt_exc,
                        )
                        break

            time.sleep(config.poll_interval)
    finally:
        mqtt.close()
        ow.close()


if __name__ == "__main__":
    main()
