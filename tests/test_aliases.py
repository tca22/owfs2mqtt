from app.discovery import load_aliases

def test_utf8_alias(tmp_path):
    p = tmp_path / "owalias.txt"
    p.write_text("283B2CAF03000005=UG_WW_Boiler_Zuleitung\n", encoding="utf-8")
    aliases = load_aliases(str(p))
    assert aliases["283B2CAF03000005"] == "UG_WW_Boiler_Zuleitung"

from app.discovery import discover, Sensor, find_removed_sensors


class FakeOW:
    def __init__(self):
        self.values = {
            "/3A.67C6697351FF/address": "3A67C6697351FFE9",
        }

    def dir(self, path):
        return ["/3A.67C6697351FF", "/bus.0", "/settings"]

    def read(self, path):
        return self.values[path]


def test_discover_unaliased_ds2413():
    sensors = discover(FakeOW(), {})
    assert len(sensors) == 1
    sensor = sensors[0]
    assert sensor.rom_id == "3A67C6697351FFE9"
    assert sensor.alias == "3A67C6697351FFE9"
    assert sensor.family == "3A"
    assert sensor.path == "/3A.67C6697351FF"


def test_find_removed_sensors_uses_rom_identity():
    previous = [
        Sensor("28AAAAAAAAAAAAAA", "temp", "28", "/28AAAAAAAAAAAAAA"),
        Sensor("3ABBBBBBBBBBBBBB", "relay", "3A", "/3ABBBBBBBBBBBBBB"),
    ]
    current = [
        Sensor("28AAAAAAAAAAAAAA", "temp", "28", "/28AAAAAAAAAAAAAA"),
    ]

    removed = find_removed_sensors(previous, current)

    assert [sensor.rom_id for sensor in removed] == ["3ABBBBBBBBBBBBBB"]


def test_find_removed_sensors_does_not_remove_new_device():
    previous = [Sensor("28AAAAAAAAAAAAAA", "temp", "28", "/28AAAAAAAAAAAAAA")]
    current = [
        Sensor("28AAAAAAAAAAAAAA", "temp", "28", "/28AAAAAAAAAAAAAA"),
        Sensor("3ABBBBBBBBBBBBBB", "relay", "3A", "/3ABBBBBBBBBBBBBB"),
    ]

    assert find_removed_sensors(previous, current) == []
