from i2cdevice import MockSMBus


def test_timer_value():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1, default_registers={
        0x0a: 0xff,  # Bits 0-7 of TIMER_VALUE,
        0x0b: 0x0f   # Bits 11-8 of TIMER_VVALUE
    }))

    assert device.get_periodic_timer_countdown_value() == 0xfff


def test_timer_status():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1, default_registers={
        0x0c: 0xff,  # Bits 0-7 of TIMER_STATUS,
        0x0d: 0x0f   # Bits 11-8 of TIMER_STATUS
    }))

    assert device.get_periodic_timer_countdown_status() == 0xfff
