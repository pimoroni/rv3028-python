from i2cdevice import MockSMBus


def test_unix_time_lsb():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1, default_registers={
        0x1b: 0xff  # Bits 0-7 of UNIX_TIME
    }))

    assert device.get_unix_time() == 0xff


def test_unix_time_msb():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1, default_registers={
        0x1b: 0x00,  # Bits 0-7 of UNIX_TIME
        0x1e: 0xff   # Bits 24-31 of UNIX_TIME
    }))

    assert device.get_unix_time() == 0xff000000
