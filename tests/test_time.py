from i2cdevice import MockSMBus
import datetime
import pytest


def test_time_and_date():
    t = datetime.time(12, 39, 7)
    d = datetime.date(2020, 2, 29)
    smbus = MockSMBus(1)
    import rv3028
    device = rv3028.RV3028(i2c_dev=smbus)
    device.set_time(t)
    device.set_date(d)
    assert device.get_time() == t
    assert device.get_date() == d

    assert smbus.regs[0x02] == 0b00010010
    assert smbus.regs[0x05] == 0b00000010
    assert smbus.regs[0x06] == 0b00100000  # 2020, but we have a year offset of +2000 internally so the BCD value is just 20


def test_invalid_time_source():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1))
    with pytest.raises(TypeError):
        device.set_time(None)


def test_invalid_date_source():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1))
    with pytest.raises(TypeError):
        device.set_date(None)


def test_invalid_datetime_source():
    import rv3028
    device = rv3028.RV3028(i2c_dev=MockSMBus(1))
    with pytest.raises(TypeError):
        device.set_time_and_date(None)
