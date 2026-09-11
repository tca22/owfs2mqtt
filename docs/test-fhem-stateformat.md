# FHEM STATE-format acceptance test

1. Add `docs/fhem-stateformat.cfg` to FHEM once.
2. Keep the documented `ow2mqtt_bridge` and `MQTT_SERVER` simple autocreate setup.
3. Delete the disposable `owfs_*` test devices, or use newly discovered
   devices.
4. Let `owfs2mqtt` publish one state cycle.
5. Verify:
   - DS18B20/DS18S20/DS1822: `STATE` is temperature formatted to 1 decimal place with `°C`.
   - pressure DS2438: `STATE` is the `pressure` value followed by `bar`.
   - other DS2438: `STATE` is the `VDD` value followed by `V`.
   - DS2413: `STATE` is `A: <PIO_A> | B: <PIO_B>`.
   - DS2401/DS1420: `STATE` is the `available` value.
6. Verify that an explicitly configured `stateFormat` is not overwritten.
7. Remove a sensor from OWServer and verify that its existing FHEM device
   remains and becomes unavailable; its `stateFormat` remains intact.
