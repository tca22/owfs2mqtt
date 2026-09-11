from dataclasses import dataclass
import os
import yaml

@dataclass
class Config:
    ow_host: str
    ow_port: int
    ow_timeout: float
    mqtt_host: str
    mqtt_port: int
    mqtt_client_id: str
    mqtt_root_topic: str
    mqtt_mode: str
    mqtt_qos: int
    mqtt_retain: bool
    poll_interval: int
    alias_file: str
    pressure_enabled: bool
    pressure_alias: str
    pressure_min_vad: float
    pressure_span_bar_at_4v: float
    pressure_bar_to_psi: float
    pressure_max_vad: float
    pressure_accuracy_divisor: float

def _env(name, default):
    return os.getenv(name, default)

def load_config(path=None):
    data = {}
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    ow = data.get("owserver", {})
    mq = data.get("mqtt", {})
    pr = data.get("pressure", {})
    formula = pr.get("formula", {})

    return Config(
        ow_host=_env("OW_SERVER_HOST", ow.get("host", "owfs")),
        ow_port=int(_env("OW_SERVER_PORT", ow.get("port", 4304))),
        ow_timeout=float(_env("OW_SERVER_TIMEOUT", ow.get("timeout", 5))),
        mqtt_host=_env("MQTT_HOST", mq.get("host", "localhost")),
        mqtt_port=int(_env("MQTT_PORT", mq.get("port", 1883))),
        mqtt_client_id=_env("MQTT_CLIENT_ID", mq.get("client_id", "ow2mqtt")),
        mqtt_root_topic=_env("MQTT_ROOT_TOPIC", mq.get("root_topic", "1-wire")).strip("/"),
        mqtt_mode=_env("MQTT_MODE", mq.get("mode", "json")).lower(),
        mqtt_qos=int(_env("MQTT_QOS", mq.get("qos", 0))),
        mqtt_retain=_env("MQTT_RETAIN", str(mq.get("retain", True))).lower() in ("1","true","yes"),
        poll_interval=int(_env("POLL_INTERVAL", data.get("poll_interval", 60))),
        alias_file=_env("ALIAS_FILE", data.get("alias_file", "/config/owalias.txt")),
        pressure_enabled=_env("PRESSURE_ENABLED", str(pr.get("enabled", True))).lower() in ("1","true","yes"),
        pressure_alias=_env("PRESSURE_ALIAS", pr.get("alias", "pressure")),
        pressure_min_vad=float(_env("PRESSURE_MIN_VAD", formula.get("min_vad", 0.5))),
        pressure_span_bar_at_4v=float(_env("PRESSURE_SPAN_BAR_AT_4V", formula.get("span_bar_at_4v", 150))),
        pressure_bar_to_psi=float(_env("PRESSURE_BAR_TO_PSI", formula.get("bar_to_psi", 0.0689476))),
        pressure_max_vad=float(_env("PRESSURE_MAX_VAD", formula.get("max_vad", 4.5))),
        pressure_accuracy_divisor=float(_env("PRESSURE_ACCURACY_DIVISOR", formula.get("accuracy_divisor", 200))),
    )
