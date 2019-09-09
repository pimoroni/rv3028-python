from i2cdevice import MockSMBus


def test_alarm_hours_24():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1, default_registers={
        0x08: 0b00100001,  # 21 hours
    }))

    assert device.get_alarm_time().hour == 21


def test_alarm_hours_12():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1, default_registers={
        0x08: 0b00010001,  # 11 hours
    }))

    assert device.get_alarm_time().hour == 11
