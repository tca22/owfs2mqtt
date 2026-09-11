import json
import sys
import types
from types import SimpleNamespace


class _FakeResultConstant:
    MQTT_ERR_SUCCESS = 0


def _client_placeholder(*args, **kwargs):
    raise AssertionError("patched in test")


_paho = types.ModuleType("paho")
_paho_mqtt = types.ModuleType("paho.mqtt")
_paho_client = types.ModuleType("paho.mqtt.client")
_paho_client.CallbackAPIVersion = SimpleNamespace(VERSION2=2)
_paho_client.MQTT_ERR_SUCCESS = 0
_paho_client.Client = _client_placeholder
_paho_mqtt.client = _paho_client
_paho.mqtt = _paho_mqtt
sys.modules.setdefault("paho", _paho)
sys.modules.setdefault("paho.mqtt", _paho_mqtt)
sys.modules.setdefault("paho.mqtt.client", _paho_client)

from app.mqtt import MQTTPublisher


class FakeResult:
    rc = 0


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.published = []
        self.will = None
    def will_set(self, topic, payload=None, qos=0, retain=False):
        self.will = (topic, payload, qos, retain)
    def connect(self, *args):
        pass
    def loop_start(self):
        pass
    def loop_stop(self):
        pass
    def disconnect(self):
        pass
    def publish(self, topic, payload, qos=0, retain=False):
        self.published.append((topic, payload, qos, retain))
        return FakeResult()


def cfg(mode="json"):
    return SimpleNamespace(
        mqtt_client_id="ow2mqtt", mqtt_root_topic="1-wire", mqtt_mode=mode,
        mqtt_qos=0, mqtt_retain=True, mqtt_host="localhost", mqtt_port=1883,
    )


def test_json_state_never_contains_literal_offline(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("app.mqtt.mqtt.Client", lambda *a, **k: fake)
    p = MQTTPublisher(cfg())
    p.publish_sensor({"alias": "T", "available": True, "temperature": 42.0})
    state = fake.published[0]
    assert state[0] == "1-wire/T/state"
    assert json.loads(state[1])["temperature"] == 42.0
    assert state[1] != "offline"
    assert fake.published[1][0] == "1-wire/T/availability"
    assert fake.published[1][1] == "online"
    assert fake.published[1][3] is False


def test_unavailable_sensor_has_json_state_and_separate_availability(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("app.mqtt.mqtt.Client", lambda *a, **k: fake)
    p = MQTTPublisher(cfg())
    p.publish_sensor({"alias": "T", "rom_id": "28X", "family": "28", "device_type": "DS18B20", "available": False})
    payload = json.loads(fake.published[0][1])
    assert fake.published[1][1] == "offline"
    assert fake.published[1][3] is False
    assert payload["available"] is False


def test_bridge_lwt_and_online(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("app.mqtt.mqtt.Client", lambda *a, **k: fake)
    p = MQTTPublisher(cfg())
    assert fake.will == ("1-wire/bridge/availability", "offline", 0, True)
    p.connect()
    assert fake.published == []


def test_bridge_availability_can_be_changed(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("app.mqtt.mqtt.Client", lambda *a, **k: fake)
    p = MQTTPublisher(cfg())
    p.publish_bridge_availability(False)
    assert fake.published[-1] == ("1-wire/bridge/availability", "offline", 0, True)
    p.publish_bridge_availability(True)
    assert fake.published[-1] == ("1-wire/bridge/availability", "online", 0, True)


def test_backend_availability_is_retained_and_reconnect_republishes_online(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("app.mqtt.mqtt.Client", lambda *a, **k: fake)
    p = MQTTPublisher(cfg())
    p.set_backend_available(True)
    assert fake.published[-1] == ("1-wire/bridge/availability", "online", 0, True)

    fake.published.clear()
    p.client.on_connect(fake, None, {}, 0, None)
    assert fake.published[-1] == ("1-wire/bridge/availability", "online", 0, True)


class FakeReasonCode:
    is_failure = False


def test_bridge_reconnect_accepts_paho_v2_reason_code(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("app.mqtt.mqtt.Client", lambda *a, **k: fake)
    p = MQTTPublisher(cfg())
    p.backend_available = True
    fake.published.clear()
    p.client.on_connect(fake, None, {}, FakeReasonCode(), None)
    assert fake.published[-1] == ("1-wire/bridge/availability", "online", 0, True)
