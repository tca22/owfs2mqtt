from .pressure import calculate_pressure

SUPPORTED = {
    "01": "DS2401",
    "18": "DS18S20",
    "22": "DS1822",
    "26": "DS2438",
    "28": "DS18B20",
    "3A": "DS2413",
    "81": "DS1420",
}

def _num(value):
    try:
        f = float(str(value).strip())
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return value

def read_sensor(client, sensor, config):
    family = sensor.family
    data = {
        "alias": sensor.alias,
        "rom_id": sensor.rom_id,
        "family": family,
        "device_type": SUPPORTED.get(family, "unknown"),
    }

    if not sensor.discovered:
        data["available"] = False
        return data

    data["available"] = True
    base = sensor.path

    if family in ("18", "22", "28"):
        data["temperature"] = _num(client.read(base + "/temperature"))

    elif family == "26":
        for field in ("VAD", "VDD", "temperature", "humidity", "current"):
            try:
                data[field] = _num(client.read(base + "/" + field))
            except Exception:
                pass
        if config.pressure_enabled and sensor.alias == config.pressure_alias and "VAD" in data:
            pressure, accuracy = calculate_pressure(
                data["VAD"],
                config.pressure_min_vad,
                config.pressure_span_bar_at_4v,
                config.pressure_bar_to_psi,
                config.pressure_max_vad,
                config.pressure_accuracy_divisor,
            )
            if pressure is not None:
                data["pressure"] = pressure
                data["accuracy"] = accuracy

    elif family == "01":
        data["present"] = True

    elif family == "81":
        data["present"] = True

    elif family == "3A":
        for field in ("PIO.A", "PIO.B", "PIO.ALL", "PIO.BYTE", "sensed.A", "sensed.B"):
            try:
                data[field.replace(".", "_")] = _num(client.read(base + "/" + field))
            except Exception:
                pass

    else:
        data["supported"] = False

    return data
