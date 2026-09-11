from types import SimpleNamespace

from app.sensors import read_sensor


class FakeOW:
    def __init__(self, values):
        self.values = values

    def read(self, path):
        return self.values[path]


def cfg():
    return SimpleNamespace(
        pressure_enabled=True,
        pressure_alias="pressure",
        pressure_min_vad=0.5,
        pressure_span_bar_at_4v=4.0,
        pressure_bar_to_psi=0.0689476,
        pressure_max_vad=4.5,
        pressure_accuracy_divisor=200,
    )


def test_ds2413_reads_pio_a_and_b():
    sensor = SimpleNamespace(
        family="3A",
        alias="relay",
        rom_id="3A1234567890ABCD",
        path="/3A1234567890ABCD",
        discovered=True,
    )
    ow = FakeOW({
        sensor.path + "/PIO.A": "1",
        sensor.path + "/PIO.B": "0",
        sensor.path + "/PIO.ALL": "1,0",
        sensor.path + "/PIO.BYTE": "1",
        sensor.path + "/sensed.A": "1",
        sensor.path + "/sensed.B": "0",
    })

    data = read_sensor(ow, sensor, cfg())

    assert data["device_type"] == "DS2413"
    assert data["available"] is True
    assert data["PIO_A"] == 1
    assert data["PIO_B"] == 0
    assert data["PIO_ALL"] == "1,0"
    assert data["PIO_BYTE"] == 1


def test_ds2413_missing_optional_property_does_not_fail():
    sensor = SimpleNamespace(
        family="3A",
        alias="relay",
        rom_id="3A1234567890ABCD",
        path="/3A1234567890ABCD",
        discovered=True,
    )
    ow = FakeOW({sensor.path + "/PIO.A": "0"})

    data = read_sensor(ow, sensor, cfg())

    assert data["PIO_A"] == 0
    assert "PIO_B" not in data


def test_ds1420_is_supported():
    sensor = SimpleNamespace(
        family="81",
        alias="USB_OneWire",
        rom_id="815108310000004A",
        path="/81.5108310000004A",
        discovered=True,
    )
    data = read_sensor(FakeOW({}), sensor, cfg())

    assert data["device_type"] == "DS1420"
    assert data["available"] is True
    assert "supported" not in data
