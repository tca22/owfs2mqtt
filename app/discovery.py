from dataclasses import dataclass


@dataclass(frozen=True)
class Sensor:
    rom_id: str
    alias: str
    family: str
    path: str
    discovered: bool = True


def load_aliases(filename):
    aliases = {}
    try:
        with open(filename, encoding="utf-8-sig") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                rom, alias = line.split("=", 1)
                rom, alias = rom.strip().upper(), alias.strip()
                if len(rom) == 16 and all(c in "0123456789ABCDEF" for c in rom) and alias:
                    aliases[rom] = alias
    except FileNotFoundError:
        # Alias mapping is optional. Discovery must not depend on owalias.txt.
        pass
    return aliases


def _rom_from_path(client, path):
    """Resolve an OWFS device path to its canonical 16-hex ROM ID."""
    try:
        address = str(client.read("/" + path + "/address")).strip().upper()
        if len(address) == 16 and all(c in "0123456789ABCDEF" for c in address):
            return address
    except Exception:
        pass

    # Some OWFS views expose the ROM as FAMILY.ID (without CRC).  Do not
    # invent the missing CRC; a full ROM is required for stable identity.
    compact = path.replace(".", "").upper()
    if len(compact) == 16 and all(c in "0123456789ABCDEF" for c in compact):
        return compact
    return None


def discover(client, aliases):
    result = []
    seen_roms = set()

    for raw in client.dir("/"):
        path = raw.strip().strip("/")
        if not path or "/" in path:
            continue

        # Ignore OWFS service entries (bus.0, settings, ...). Device entries
        # are identified dynamically through their OWFS address property.
        rom = _rom_from_path(client, path)
        if not rom:
            continue

        family = rom[:2]
        alias = aliases.get(rom, rom)
        seen_roms.add(rom)
        result.append(Sensor(rom, alias, family, "/" + path))

    # Keep explicitly configured aliases visible as unavailable when a known
    # device is absent. This preserves the existing availability behaviour.
    for rom, alias in aliases.items():
        if rom not in seen_roms:
            result.append(Sensor(rom, alias, rom[:2], "/" + alias, discovered=False))

    return result


def find_removed_sensors(previous, current):
    """Return previously known sensors that are absent from a successful discovery."""
    current_roms = {sensor.rom_id for sensor in current}
    return [sensor for sensor in previous if sensor.rom_id not in current_roms]
