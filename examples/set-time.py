#!/usr/bin/env python

import rv3028
import time
import datetime

print("""set-time.py - Sets RTC with current time for your system and
enables battery backup to preserve the time when power is off.

Press Ctrl+C to exit.

""")

# Create RV3028 instance
rtc = rv3028.RV3028()

# Switches RTC to backup battery if VCC goes below 2V
# Other settings: 'switchover_disabled', 'direct_switching_mode', 'standby_mode'
rtc.set_battery_switchover('level_switching_mode')

try:
    current_system_time = datetime.datetime.now()
    # Time and date may also be set as a tuple (hour, minute, second, year, month, date)
    rtc.set_time_and_date(current_system_time)

    while True:
        rtc_time = rtc.get_time_and_date()
        print("The time is: {:02d}:{:02d}:{:02d} on :{:02d}/{:02d}/{:02d}".format(rtc_time.hour, rtc_time.minute, rtc_time.second, rtc_time.day, rtc_time.month, rtc_time.year))
        time.sleep(1)

except KeyboardInterrupt:
    pass
