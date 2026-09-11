# DS2413 integration test with OWServer fake adapter

OWFS documents `--fake=devices` as a simulated 1-Wire bus. Family code `3A` represents a DS2413. The fake adapter creates a random device ID and random property values, so this test validates discovery, field mapping and value domains rather than fixed values.

## Start a dedicated test OWServer

Run a separate OWServer instance so the productive `owfs` container remains untouched. For example, on a test host/container:

```sh
owserver --fake=3A -p 4305
```

If the installed OWFS build uses the space-separated syntax shown by its help output, the equivalent form is:

```sh
owserver --fake 3A -p 4305
```

Verify the simulated device:

```sh
owdir -s 127.0.0.1:4305 /
```

Then inspect its PIO properties:

```sh
owdir -s 127.0.0.1:4305 /<DS2413-ROM>/
owread -s 127.0.0.1:4305 /<DS2413-ROM>/PIO.A
owread -s 127.0.0.1:4305 /<DS2413-ROM>/PIO.B
```

The OWFS DS2413 interface defines `PIO.A` and `PIO.B` as the switch-state properties and `sensed.A/B` as the actual pin logic-level properties.

## OW2MQTT test

Point a disposable OW2MQTT test instance at the fake OWServer (`OW_SERVER_HOST` / `OW_SERVER_PORT=4305`) and use a dedicated alias entry for the simulated ROM. Verify that the resulting JSON contains:

```json
{
  "device_type": "DS2413",
  "PIO_A": 0,
  "PIO_B": 1
}
```

The actual values are expected to vary with the fake adapter.

## FHEM acceptance criteria

The generated `owfs_<alias>` device must contain:

- `PIO_A`
- `PIO_B`

and the FHEM presentation should use:

```text
A: <PIO_A> | B: <PIO_B>
```

The physical DS2413 hardware test remains a later confirmation test, not a prerequisite for completing the software integration test.
