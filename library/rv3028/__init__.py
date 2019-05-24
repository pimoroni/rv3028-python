import time
from i2cdevice import Device, Register, BitField
from i2cdevice.adapter import Adapter, LookupAdapter


__version__ = '0.0.1'


class SensorDataAdapter(Adapter):
    """Convert from 16-bit sensor data with crazy offset"""
    def __init__(self, bit_resolution=14):
        self.bit_resolution = bit_resolution

    def _encode(self, value):
        return value

    def _decode(self, value):
        LSB = (value & 0xFF00) >> 10
        MSB = (value & 0x00FF) << 6
        # print (bin(MSB),bin(LSB))
        return MSB + LSB


class InterruptLookupAdapter(Adapter):
    """Special version of the 
    look up adapter that 
    allows for multipule 
    values to be set at once"""
    def __init__(self, lookup_table):
        self.lookup_table = lookup_table

    def _decode(self, value):
        return_list = []

        for bit_index in range(8):
            if (value & (1 << bit_index) != 0):
                index = list(self.lookup_table.values()).index(1 << bit_index)
                return_list.append(list(self.lookup_table.keys())[index])

        return return_list

    def _encode(self, value):
        return_value = 0x00

        try:
            for item in value:
                return_value = return_value | self.lookup_table[item]
        except TypeError:
            raise ValueError('interrupt settings require a list')

        return return_value


class RV3028:
    def __init__(self, i2c_addr=0x26, i2c_dev=None):
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._is_setup = False
        # Device definition
        self._rv3028 = Device([0x52], i2c_dev=self._i2c_dev,
                bit_width=8, registers=(
                Register('SECONDS', 0x00, fields=(
                    BitField('seconds', 0x7F),
                )),
                Register('MINUTES', 0x01, fields=(
                    BitField('minutes', 0x7F),
                )),
                Register('HOURS', 0x02, fields=(
                    BitField('24hours', 0b00011111),
                    BitField('12hours', 0b00001111),
                    BitField('am_pm', 0x00010000),
                )),
                Register('WEEKDAY', 0x03, fields=(
                    BitField('weekday', 0b00000111),
                )),
                Register('DATE', 0x04, fields=(
                    BitField('date', 0b00011111),
                )),
                Register('MONTH', 0x05, fields=(
                    BitField('month', 0b00001111),
                )),
                Register('YEAR', 0x06, fields=(
                    BitField('year', 0xFF),
                )),
                Register('ALARM_MINUTES', 0x07, fields=(
                    BitField('minutes_alarm_enable', 0b10000000),
                    BitField('minutes', 0x7F),
                )),
                Register('ALARM_HOURS', 0x08, fields=(
                    BitField('hours_alarm_enable', 0b10000000),
                    BitField('24hours', 0b00011111),
                    BitField('12hours', 0b00001111),
                    BitField('am_pm', 0x00010000),
                )),
                Register('ALARM_WEEKDAY', 0x09, fields=(
                    BitField('weekday_alarm_enable', 0b10000000)
                    BitField('weekday', 0b00000111),
                    BitField('date', 0b00000111)
                )),
                Register('TIMER_VALUE_LSB', 0x0A, fields=(
                    BitField('value', 0xFF),
                )),
                Register('TIMER_VALUE_MSB', 0x0B, fields=(
                    BitField('value', 0b00001111),
                )),
                Register('TIMER_STATUS_LSB', 0x0C, fields=(
                    BitField('value', 0xFF),
                )),
                Register('TIMER_STATUS_MSB', 0x0D, fields=(
                    BitField('value', 0b00001111),
                )),
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
                    BitField('timer_frequency_selection', 0b00000011, adapter=LookupAdapter{
                        '4036Hz' : 0b00,  # 214.14us
                        '63Hz' : 0b01,    # 15.625ms
                        '1Hz' : 0b10,     # 1s
                        '0.016Hz':0b11    # 60s
                        }),
                )),
                Register('CONTROL_2', 0x10, fields=(
                    BitField('value', 0xFF),
                    BitField('timestamp_enable', 0b10000000),
                    BitField('interrupt_controlled_output_enable', 0b01000000),
                    BitField('periodic_time_update_interupt_enable', 0b00100000),
                    BitField('periodic_countdown_timer_interupt_enable', 0b00010000),
                    BitField('alarm_interupt_enable', 0b00001000),
                    BitField('external_event_interrupt_enable', 0b00000100),
                    BitField('24_12_hours_select', 0b00000010),
                    BitField('reset', 0b00000001),
                )),
                Register('GENERAL_PURPOSE_STOREAGE_REGISTER', 0x11, fields=(
                    BitField('value', 0b01111111),
                )),
                Register('CLOCK_INTERRUPT_MASK', 0x12, fields=(
                    BitField('value', 0x0F),
                    BitField('clock_output_when_event_interrupt', 0b00001000),
                    BitField('clock_output_when_alarm_interrupt', 0b00000100),
                    BitField('clock_output_when_countdown_interrupt', 0b00000010),
                    BitField('clock_output_when_peroidic_interrupt', 0b00000001),
                )),
                Register('EVENT_CONTROL', 0x13, fields=(
                    BitField('value', 0xFF),
                    BitField('event_high_low_detection', 0b01000000),
                    BitField('event_filtering_time', 0b00110000, adapter=LookupAdapter{
                        'no_filtering' : 0b00,
                        '3.9ms' : 0b01,
                        '15.6ms' : 0b10,
                        '125ms':0b11
                        }),
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
                    BitField('24hours', 0b00011111),
                    BitField('12hours', 0b00001111),
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
                    BitField('value', 0xFF),
                )),
                Register('UNIX_TIME_1', 0x1C, fields=(
                    BitField('value', 0xFF),
                )),
                Register('UNIX_TIME_2', 0x1D, fields=(
                    BitField('value', 0xFF),
                )),
                Register('UNIX_TIME_3', 0x1E, fields=(
                    BitField('value', 0xFF),
                )),
                Register('USER_RAM_1', 0x1F, fields=(
                    BitField('value', 0b11111111),
                )),
                Register('USER_RAM_2', 0x20, fields=(
                    BitField('value', 0b11111111),
                )),
                Register('PASSWORD', 0x21, fields=(
                    BitField('value', 0xFF),
                )),
                Register('PASSWORD_1', 0x22, fields=(
                    BitField('value', 0xFF),
                )),
                Register('PASSWORD_2', 0x23, fields=(
                    BitField('value', 0xFF),
                )),
                Register('PASSWORD_3', 0x24, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_ADDRESS', 0x25, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_DATA', 0x26, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_COMMAND', 0x27, fields=(
                    BitField('command', 0xFF, adapter=LookupAdapter{
                        'first_command' : 0x00,
                        'write_all_configuration_to_eeprom' : 0x11,
                        'read_all_configuration_from_eeprom' : 0x12,
                        'write_one_byte_to_eeprom_address' : 0x21,
                        'read_one_byte_from_eeprom_address' :0x22
                        }),
                )),
                Register('PARTID', 0x28, fields=(
                    BitField('id', 0xFF),
                )),
                Register('EEPROM_PASSWORD_ENABLE', 0x30, fields=(
                    BitField('value', 0xFF),  # write 0xFF to this regester to enable eeprom password
                )),
                Register('EEPROM_PASSWORD', 0x31, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_PASSWORD_1', 0x32, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_PASSWORD_2', 0x33, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_PASSWORD_3', 0x34, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_CLKOUT', 0x35, fields=(
                    BitField('value', 0xFF),
                    BitField('clkout_output', 0b10000000),
                    BitField('clkout_synchronized', 0b01000000),
                    BitField('power_on_reset_interrput_enable', 0b00001000),
                    BitField('clkout_frequency_selection', 0b00000111, adapter=LookupAdapter{
                        '32.768kHz' : 0b000,
                        '8192Hz' : 0b001,
                        '1024Hz' : 0b010,
                        '64Hz':0b011,
                        '32Hz' : 0b100,
                        '1Hz' : 0b101,
                        'periodic_countdown_timer_interupt' : 0b110,
                        'clkout_low':0b111,
                        }), 
                )),
                Register('EEPROM_OFFSET', 0x36, fields=(
                    BitField('value', 0xFF),
                )),
                Register('EEPROM_BACKUP', 0x37, fields=(
                    BitField('value', 0xFF),
                    BitField('ee_offset', 0b10000000),
                    BitField('backup_switchver_interrupt_enable', 0b00100000),
                    BitField('trickle_charger_enable', 0b00010000),
                    BitField('fast_edge_detection', 0b00001000),
                    BitField('automatic_backup_switchover', 0b00000100),
                    BitField('trickle_charger_series_resistance', 0b00000011, adapter=LookupAdapter{
                        '1kOhm' : 0b00,  
                        '3kOhm' : 0b01,    
                        '6kOhm' : 0b10,    
                        '11kOhm' : 0b11   
                        }),
                )),
                self.pimoroni_eeprom_data_start = 0x00
                self.pimoroni_eeprom_data_end =  0x06                

        ))

