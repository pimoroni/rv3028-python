import sys
from i2cdevice import MockSMBus
import mock


def test_setup():
    sys.modules['smbus'] = mock.Mock()
    sys.modules['smbus'].SMBus = MockSMBus
    import rv3028
    device = rv3028.RV3028()
    device.reset()
    device.get_id()
    device.set_time_and_date((2001, 1, 1, 1, 1, 1))
    current = device.get_time_and_date()
    device.set_time_and_date(current)
    device.set_unix_time(0xFF)
    unix_time = device.get_unix_time()
    device.set_unix_time(unix_time)
    device.set_alarm_time((1, 1, 1, 1), 1)
    device.get_alarm_time()
    device.set_alarm_setting('disabled_monthly')
    device.get_alarm_setting()
    device.get_alarm_interrupt()
    device.clear_alarm_interrupt()
    for settings in device.alarm_frequency:
        device.set_alarm_setting(settings)
        device.get_alarm_setting()
    device.set_battery_switchover('level_switching_mode')
    device.get_battery_switchover()
    device.clear_all_interrupts()
    device.get_all_interrupts()
    device.stop_periodic_timer()
    device.set_periodic_timer_frequency('1Hz')
    device.get_periodic_timer_frequency()
    device.set_periodic_timer_countdown_value(0xFFFF)
    device.get_periodic_timer_countdown_value()
    device.get_periodic_timer_countdown_status()
    device.start_periodic_timer()
    device.clear_periodic_countdown_timer_interrupt()
    device.get_periodic_countdown_timer_interrupt()

    del device
