import datetime

import pytest
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


def test_set_alarm_time_tuple():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1))
    device.set_alarm_time((1, 12, 44))
    device.set_alarm_time((12, 44), weekday=1)


def test_set_alarm_time():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1))
    device.set_alarm_time(datetime.datetime(2020, 2, 29, 12, 44))
    device.set_alarm_time(datetime.datetime(2020, 2, 29, 12, 44), weekday=1)


def test_invalid_time_source():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1))
    with pytest.raises(TypeError):
        device.set_alarm_time(None)
    with pytest.raises(TypeError):
        device.set_alarm_time(None, weekday=1)
