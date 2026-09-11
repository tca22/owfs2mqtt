import json
import paho.mqtt.client as mqtt


class MQTTConnectionError(RuntimeError):
    pass


class MQTTPublisher:
    def __init__(self, config):
        self.config = config
        self.root = config.mqtt_root_topic
        self.bridge_availability_topic = f"{self.root}/bridge/availability"
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=config.mqtt_client_id,
        )
        # One MQTT connection has one LWT. It represents bridge availability.
        self.backend_available = False
        self.client.will_set(
            self.bridge_availability_topic,
            payload="offline",
            qos=config.mqtt_qos,
            retain=True,
        )
        self.client.on_connect = self._on_connect

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        # Paho invokes this again after an automatic reconnect. Re-publish
        # application availability only if the OWServer backend is known to be
        # healthy. MQTT transport availability itself is covered by the LWT.
        # Paho MQTT v2 passes a ReasonCode object here, not an int.
        # Keep a small fallback for test doubles / older callback shapes.
        success = (
            not reason_code.is_failure
            if hasattr(reason_code, "is_failure")
            else int(reason_code) == 0
        )
        if success and self.backend_available:
            try:
                self.publish_bridge_availability(True)
            except Exception:
                pass

    def connect(self):
        self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
        self.client.loop_start()

    def set_backend_available(self, available):
        self.backend_available = bool(available)
        self.publish_bridge_availability(self.backend_available)

    def publish_bridge_availability(self, available):
        """Publish application/OWServer availability.

        MQTT connectivity itself is represented by the LWT; this retained
        topic additionally represents whether the OWServer backend is usable.
        """
        self.publish(
            self.bridge_availability_topic,
            "online" if available else "offline",
        )

    def publish_sensor(self, data):
        alias = data["alias"]
        root = self.root

        # Publish state before availability. This is important for FHEM: the
        # first message for a new sensor should be the JSON state, so
        # autocreate=complex can recognize the payload as JSON.
        available = bool(data.get("available", False))

        if self.config.mqtt_mode in ("flat", "legacy"):
            for key, value in data.items():
                if key in ("alias",):
                    continue
                self.publish(f"{root}/{alias}/{key}", value)
        else:
            self.publish(
                f"{root}/{alias}/state",
                json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            )

        # Availability is intentionally not retained. The retained JSON state
        # is sufficient for restart/autocreate, while a retained availability
        # message could arrive before state and recreate the original FHEM
        # autocreate ordering problem.
        self.publish(
            f"{root}/{alias}/availability",
            "online" if available else "offline",
            retain=False,
        )

    def publish_sensor_unavailable(self, sensor):
        device_types = {
            "01": "DS2401",
            "18": "DS18S20",
            "22": "DS1822",
            "26": "DS2438",
            "28": "DS18B20",
            "3A": "DS2413",
            "81": "DS1420",
        }
        data = {
            "alias": sensor.alias,
            "rom_id": sensor.rom_id,
            "family": sensor.family,
            "device_type": device_types.get(sensor.family, "unknown"),
            "available": False,
        }
        self.publish_sensor(data)

    def publish(self, topic, value, retain=None):
        if value is None:
            return
        payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        if retain is None:
            retain = self.config.mqtt_retain
        result = self.client.publish(
            topic,
            payload,
            qos=self.config.mqtt_qos,
            retain=retain,
        )
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise MQTTConnectionError(f"MQTT publish failed rc={result.rc}: {topic}")

    def close(self):
        # Graceful shutdown: publish offline explicitly. Unexpected shutdowns
        # are handled by the MQTT LWT configured in __init__.
        try:
            self.publish(self.bridge_availability_topic, "offline")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
