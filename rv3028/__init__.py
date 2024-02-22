import time
from i2cdevice import Device, Register, BitField
from i2cdevice.adapter import Adapter, LookupAdapter, U16ByteSwapAdapter
import datetime

__version__ = '0.0.5'


class BCDAdapter(Adapter):

    def _decode(self, value):
        upper = ((value & 0xF0) >> 4) * 10
        lower = (value & 0x0F)

        return upper + lower

    def _encode(self, value):
        upper = (int(value / 10)) << 4
        lower = value % 10

        return upper | lower


class ReverseBytesAdapter(Adapter):
    def __init__(self, number_of_bytes):
        self._number_of_bytes = number_of_bytes

    def _decode(self, value):
        result = 0
        for x in range(self._number_of_bytes):
            result <<= 8
            result |= value & 0xff
            value >>= 8
        return result

    def _encode(self, value):
        result = 0
        for x in range(self._number_of_bytes):
            result <<= 8
            result |= value & 0xff
            value >>= 8
        return result


class RV3028:
    def __init__(self, i2c_addr=0x26, i2c_dev=None):
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._is_setup = False

        self._rv3028 = Device([0x52], i2c_dev=self._i2c_dev, bit_width=8, registers=(
            Register('SECONDS', 0x00, fields=(
                BitField('seconds', 0x7F, adapter=BCDAdapter()),
            )),
            Register('MINUTES', 0x01, fields=(
                BitField('minutes', 0x7F, adapter=BCDAdapter()),
            )),
            Register('HOURS', 0x02, fields=(
                BitField('t24hours', 0b00111111, adapter=BCDAdapter()),
                BitField('t12hours', 0b00011111, adapter=BCDAdapter()),
                BitField('am_pm', 0b00100000),
            )),
            Register('WEEKDAY', 0x03, fields=(
                BitField('weekday', 0b00000111),
            )),
            Register('DATE', 0x04, fields=(
                BitField('date', 0b00111111, adapter=BCDAdapter()),
            )),
            Register('MONTH', 0x05, fields=(
                BitField('month', 0b00011111, adapter=BCDAdapter()),
            )),
            Register('YEAR', 0x06, fields=(
                BitField('year', 0xFF, adapter=BCDAdapter()),
            )),
            Register('ALARM_MINUTES', 0x07, fields=(
                BitField('minutes_alarm_enable', 0b10000000),
                BitField('minutes', 0x7F, adapter=BCDAdapter()),
            )),
            Register('ALARM_HOURS', 0x08, fields=(
                BitField('hours_alarm_enable', 0b10000000, adapter=BCDAdapter()),
                BitField('t24hours', 0b00111111, adapter=BCDAdapter()),
                BitField('t12hours', 0b00011111, adapter=BCDAdapter()),
                BitField('am_pm', 0b00100000),
            )),
            Register('ALARM_WEEKDAY', 0x09, fields=(
                BitField('weekday_alarm_enable', 0b10000000, adapter=BCDAdapter()),
                BitField('weekday', 0b00000111),
                BitField('date', 0b00111111)
            )),
            Register('TIMER_VALUE', 0x0A, fields=(
                BitField('value', 0xFF0F, adapter=U16ByteSwapAdapter()),
            ), bit_width=16),
            Register('TIMER_STATUS', 0x0C, fields=(
                BitField('value', 0xFF0F, adapter=U16ByteSwapAdapter()),
            ), bit_width=16),
            Register('STATUS', 0x0E, fields=(
                BitField('value', 0xFF),
                BitField('eeprom_busy_flag', 0b10000000),
                BitField('clock_output_interrupt_flag', 0b01000000),
                BitField('backup_switch_flag', 0b00100000),
                BitField('periodic_time_update_flag', 0b00010000),
                BitField('periodic_countdown_timer_flag', 0b00001000),
                BitField('alarm_flag', 0b00000100),
                BitField('external_event_flag', 0b00000010),
                BitField('power_on_reset_flag', 0b00000001),
            )),
            Register('CONTROL_1', 0x0F, fields=(
                BitField('value', 0xFF),
                BitField('timer_repeat', 0b10000000),
                BitField('weekday_date_alarm', 0b00100000),
                BitField('update_interrupt', 0b00010000),
                BitField('eeprom_memory_refresh_disable', 0b00001000),
                BitField('periodic_countdown_timer_enable', 0b00000100),
                BitField('timer_frequency_selection', 0b00000011, adapter=LookupAdapter({
                    '4036Hz': 0b00,  # 214.14us
                    '63Hz': 0b01,    # 15.625ms
                    '1Hz': 0b10,     # 1s
                    '0.016Hz': 0b11  # 60s
                })),
            )),
            Register('CONTROL_2', 0x10, fields=(
                BitField('value', 0xFF),
                BitField('timestamp_enable', 0b10000000),
                BitField('interrupt_controlled_output_enable', 0b01000000),
                BitField('periodic_time_update_interupt_enable', 0b00100000),
                BitField('periodic_countdown_timer_interupt_enable', 0b00010000),
                BitField('alarm_interupt_enable', 0b00001000),
                BitField('external_event_interrupt_enable', 0b00000100),
                BitField('select_24_12_hours', 0b00000010),
                BitField('reset', 0b00000001),
            )),
            Register('GENERAL_PURPOSE_STORAGE_REGISTER', 0x11, fields=(
                BitField('value', 0b01111111),
            )),
            Register('CLOCK_INTERRUPT_MASK', 0x12, fields=(
                BitField('value', 0x0F),
                BitField('clock_output_when_event_interrupt', 0b00001000),
                BitField('clock_output_when_alarm_interrupt', 0b00000100),
                BitField('clock_output_when_countdown_interrupt', 0b00000010),
                BitField('clock_output_when_periodic_interrupt', 0b00000001),
            )),
            Register('EVENT_CONTROL', 0x13, fields=(
                BitField('value', 0xFF),
                BitField('event_high_low_detection', 0b01000000),
                BitField('event_filtering_time', 0b00110000, adapter=LookupAdapter({
                    'no_filtering': 0b00,
                    '3.9ms': 0b01,
                    '15.6ms': 0b10,
                    '125ms': 0b11
                })),
                BitField('timestamp_reset', 0b00000100),
                BitField('timestamp_overwrite', 0b00000010),
                BitField('timestamp_source', 0b00000001),
            )),
            Register('TIMESTAMP_COUNT', 0x14, fields=(
                BitField('value', 0xFF),
            )),
            Register('TIMESTAMP_SECONDS', 0x15, fields=(
                BitField('seconds', 0x7F),
            )),
            Register('TIMESTAMP_MINUTES', 0x16, fields=(
                BitField('minutes', 0x7F),
            )),
            Register('TIMESTAMP_HOURS', 0x17, fields=(
                BitField('t24hours', 0b00111111),
                BitField('t12hours', 0b00001111),
                BitField('am_pm', 0x00010000),
            )),
            Register('TIMESTAMP_DATE', 0x18, fields=(
                BitField('date', 0b00011111),
            )),
            Register('TIMESTAMP_MONTH', 0x19, fields=(
                BitField('month', 0b00001111),
            )),
            Register('TIMESTAMP_YEAR', 0x1A, fields=(
                BitField('year', 0xFF),
            )),
            Register('UNIX_TIME', 0x1B, fields=(
                BitField('value', 0xFFFFFFFF, adapter=ReverseBytesAdapter(4)),
            ), bit_width=32),
            Register('USER_RAM', 0x1F, fields=(
                BitField('one', 0x00FF),
                BitField('two', 0xFF00),
            ), bit_width=16),
            Register('PASSWORD', 0x21, fields=(
                BitField('value', 0xFFFFFFFF),
            ), bit_width=32),
            Register('EEPROM_ADDRESS', 0x25, fields=(
                BitField('value', 0xFF),
            )),
            Register('EEPROM_DATA', 0x26, fields=(
                BitField('value', 0xFF),
            )),
            Register('EEPROM_COMMAND', 0x27, fields=(
                BitField('command', 0xFF, adapter=LookupAdapter({
                    'first_command': 0x00,
                    'write_all_configuration_to_eeprom': 0x11,
                    'read_all_configuration_from_eeprom': 0x12,
                    'write_one_byte_to_eeprom_address': 0x21,
                    'read_one_byte_from_eeprom_address': 0x22
                })),
            )),
            Register('PART', 0x28, fields=(
                BitField('id', 0xF0),
                BitField('version', 0x0F)
            )),
            Register('EEPROM_PASSWORD_ENABLE', 0x30, fields=(
                BitField('value', 0xFF),  # Write 0xFF to this register to enable EEPROM password
            )),
            Register('EEPROM_PASSWORD', 0x31, fields=(
                BitField('value', 0xFFFFFFFF),
            ), bit_width=32),
            Register('EEPROM_CLKOUT', 0x35, fields=(
                BitField('value', 0xFF),
                BitField('clkout_output', 0b10000000),
                BitField('clkout_synchronized', 0b01000000),
                BitField('power_on_reset_interrupt_enable', 0b00001000),
                BitField('clkout_frequency_selection', 0b00000111, adapter=LookupAdapter({
                    '32.768kHz': 0b000,
                    '8192Hz': 0b001,
                    '1024Hz': 0b010,
                    '64Hz': 0b011,
                    '32Hz': 0b100,
                    '1Hz': 0b101,
                    'periodic_countdown_timer_interrupt': 0b110,
                    'clkout_low': 0b111,
                })),
            )),
            Register('EEPROM_OFFSET', 0x36, fields=(
                BitField('value', 0xFF),
            )),
            Register('EEPROM_BACKUP', 0x37, fields=(
                BitField('value', 0xFF),
                BitField('ee_offset', 0b10000000),
                BitField('backup_switchover_interrupt_enable', 0b01000000),
                BitField('trickle_charger_enable', 0b00100000),
                BitField('fast_edge_detection', 0b00010000),
                BitField('automatic_battery_switchover', 0b00001100, adapter=LookupAdapter({
                    'switchover_disabled': 0b00,
                    'direct_switching_mode': 0b01,
                    'standby_mode': 0b10,
                    'level_switching_mode': 0b11
                })),
                BitField('trickle_charger_series_resistance', 0b00000011, adapter=LookupAdapter({
                    '1kOhm': 0b00,
                    '3kOhm': 0b01,
                    '6kOhm': 0b10,
                    '11kOhm': 0b11
                })),
            ))


        ))
        self.enable_12hours = self._rv3028.get('CONTROL_2').select_24_12_hours
        self.alarm_frequency = {
            'disabled_weekly': 0b0111,
            'disabled_monthly': 0b1111,
            'hourly_on_minute': 0b110,
            'daily_on_hour': 0b101,
            'daily_on_hour_and_minute': 0b011,
            'weekly': 0b0011,
            'weekly_on_minute': 0b0010,
            'weekly_on_hour': 0b0001,
            'weekly_on_hour_and_minute': 0b0000,
            'monthly': 0b1011,
            'monthly_on_minute': 0b1010,
            'monthly_on_hour': 0b1001,
            'monthly_on_hour_and_minute': 0b1000
        }

    def reset(self):
        self._rv3028.set('CONTROL_2', reset=True)
        time.sleep(0.01)

    def get_id(self):
        part = self._rv3028.get('PART')
        return part.id, part.version

    def get_time(self):
        datetime_object = self.get_time_and_date()
        return datetime_object.time()

    def set_time(self, t):
        if isinstance(t, datetime.datetime) or isinstance(t, datetime.time):
            self._rv3028.set('HOURS', t24hours=t.hour)
            self._rv3028.set('MINUTES', minutes=t.minute)
            self._rv3028.set('SECONDS', seconds=t.second)
        elif type(t) == tuple:
            self._rv3028.set('HOURS', t24hours=t[0])
            self._rv3028.set('MINUTES', minutes=t[1])
            self._rv3028.set('SECONDS', seconds=t[2])
        else:
            raise TypeError('Time needs to be given as datetime.datetime object, or tuple (hour, minute, seconds) type used: {0}'.format(type(t)))

    def get_date(self):
        datetime_object = self.get_time_and_date()
        return datetime_object.date()

    def set_date(self, date):
        if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
            self._rv3028.set('YEAR', year=date.year - 2000)
            self._rv3028.set('MONTH', month=date.month)
            self._rv3028.set('DATE', date=date.day)
        elif type(date) == tuple:
            self._rv3028.set('YEAR', year=date[0] - 2000)
            self._rv3028.set('MONTH', month=date[1])
            self._rv3028.set('DATE', date=date[2])
        else:
            raise TypeError('Date needs to be given as datetime.datetime object, datetime.date object, or tuple (year, month, day) type used: {0}'.format(type(date)))

    def set_time_and_date(self, time_and_date):
        if isinstance(time_and_date, datetime.datetime):
            self.set_date(time_and_date)
            self.set_time(time_and_date)

        elif type(time_and_date) == tuple:
            self.set_date(time_and_date[:3])
            self.set_time(time_and_date[3:])

        else:
            raise TypeError('Time needs to be given as datetime.datetime object, or tuple (year, month, day, hour, minute, seconds) type used: {0}'.format(type(time_and_date)))

    def get_time_and_date(self):
        return datetime.datetime(
            self._rv3028.get('YEAR').year + 2000,
            self._rv3028.get('MONTH').month,
            self._rv3028.get('DATE').date,
            self._rv3028.get('HOURS').t24hours,
            self._rv3028.get('MINUTES').minutes,
            self._rv3028.get('SECONDS').seconds)

    def get_unix_time(self):
        return self._rv3028.get('UNIX_TIME').value

    def set_unix_time(self, value):
        self._rv3028.set('UNIX_TIME', value=value)

    def set_battery_switchover(self, value):
        self._rv3028.set('EEPROM_BACKUP', automatic_battery_switchover=value)

    def get_battery_switchover(self):
        return self._rv3028.get('EEPROM_BACKUP').automatic_battery_switchover

    def start_periodic_timer(self):
        self._rv3028.set('CONTROL_1', periodic_countdown_timer_enable=True)

    def stop_periodic_timer(self):
        self._rv3028.set('CONTROL_1', periodic_countdown_timer_enable=False)

    def get_periodic_timer_frequency(self):
        return self._rv3028.get('CONTROL_1').timer_frequency_selection

    def set_periodic_timer_frequency(self, value):
        self._rv3028.set('CONTROL_1', timer_frequency_selection=value)

    def set_periodic_timer_countdown_value(self, value):
        self._rv3028.set('TIMER_VALUE', value=value)

    def get_periodic_timer_countdown_value(self):
        return self._rv3028.get('TIMER_VALUE').value

    def get_periodic_timer_countdown_status(self):
        return self._rv3028.get('TIMER_STATUS').value

    def clear_all_interrupts(self):
        self._rv3028.set('STATUS', value=0)

    def clear_periodic_countdown_timer_interrupt(self):
        self._rv3028.set('STATUS', periodic_countdown_timer_flag=0)

    def clear_alarm_interrupt(self):
        self._rv3028.set('STATUS', alarm_flag=0)

    def get_all_interrupts(self):
        return self._rv3028.get('STATUS').value

    def get_periodic_countdown_timer_interrupt(self):
        return self._rv3028.get('STATUS').periodic_countdown_timer_flag

    def get_alarm_interrupt(self):
        return self._rv3028.get('STATUS').alarm_flag

    def wait_for_periodic_timer_interrupt(self, value):
        """Wait for a periodic timer countdown.

        The countdown period in seconds is equal to the value/timer frequency.

        """
        self.stop_periodic_timer()
        self._rv3028.set('TIMER_VALUE', value=value)
        self._rv3028.set('STATUS', periodic_countdown_timer_flag=False)
        self.start_periodic_timer()
        while not self._rv3028.get('STATUS').periodic_countdown_timer_flag:
            time.sleep(0.001)

    def get_alarm_setting(self):
        setting = self._rv3028.get('ALARM_MINUTES').minutes_alarm_enable
        setting |= (self._rv3028.get('ALARM_HOURS').hours_alarm_enable << 1)
        setting |= (self._rv3028.get('ALARM_WEEKDAY').weekday_alarm_enable << 2)
        setting |= (self._rv3028.get('CONTROL_1').weekday_date_alarm << 3)
        return_value = [key for (key, value) in self.alarm_frequency.items() if value == setting]
        return return_value

    def set_alarm_setting(self, setting):
        self._rv3028.set('ALARM_MINUTES', minutes_alarm_enable=self.alarm_frequency.get(setting) & 0b0001)
        self._rv3028.set('ALARM_HOURS', hours_alarm_enable=(self.alarm_frequency.get(setting) & 0b0010) >> 1)
        self._rv3028.set('ALARM_WEEKDAY', weekday_alarm_enable=(self.alarm_frequency.get(setting) & 0b0100) >> 2)
        self._rv3028.set('CONTROL_1', weekday_date_alarm=(self.alarm_frequency.get(setting) & 0b1000) >> 3)

    def set_alarm_time(self, datetime_object, weekday=0):
        if weekday == 0:
            if isinstance(datetime_object, datetime.datetime):
                self._rv3028.set('ALARM_WEEKDAY', date=datetime_object.day)
                self._rv3028.set('ALARM_HOURS', t24hours=datetime_object.hour)
                self._rv3028.set('ALARM_MINUTES', minutes=datetime_object.minute)

            elif type(datetime_object) == tuple:
                self._rv3028.set('ALARM_WEEKDAY', date=datetime_object[0])
                self._rv3028.set('ALARM_HOURS', t24hours=datetime_object[1])
                self._rv3028.set('ALARM_MINUTES', minutes=datetime_object[2])

            else:
                raise TypeError('Time needs to be given as datetime.datetime object or tuple (hour, minute, date) type used: {0}'.format(type(time)))
        else:
            if isinstance(datetime_object, datetime.datetime):
                self._rv3028.set('ALARM_WEEKDAY', weekday=weekday)
                self._rv3028.set('ALARM_HOURS', t24hours=datetime_object.hour)
                self._rv3028.set('ALARM_MINUTES', minutes=datetime_object.minute)

            elif type(datetime_object) == tuple:
                self._rv3028.set('ALARM_WEEKDAY', weekday=weekday)
                self._rv3028.set('ALARM_HOURS', t24hours=datetime_object[0])
                self._rv3028.set('ALARM_MINUTES', minutes=datetime_object[1])
            else:
                raise TypeError('Time needs to be given as datetime.datetime object or tuple (hour, minute) and a 0 > weekday int type used: {0}'.format(type(time)))

    def get_alarm_time(self):
        return datetime.time(
            self._rv3028.get('ALARM_HOURS').t24hours,
            self._rv3028.get('ALARM_MINUTES').minutes,
            self._rv3028.get('ALARM_WEEKDAY').weekday)


if __name__ == "__main__":

    import smbus
    bus = smbus.SMBus(1)
    rtc = RV3028(i2c_dev=bus)
    print('Part ID: {0[0]} Revision: {0[1]}'.format(rtc.get_id()))
