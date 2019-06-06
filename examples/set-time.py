#!/usr/bin/env python

import rv3028
import time
import datetime

print("""set-time.py - Sets RTC with current time for your system and enble battery back-up to preserve the time when power is off

Press Ctrl+C to exit.

""")

rtc = rv3028.RV3028()
# Switches rtc to backup battery of vcc goes below 2V other settings 'switchover_disabled', 'direct_switching_mode', 'standy_mode'
rtc.set_battery_switchover('level_switching_mode')

try:
    current_system_time = datetime.datetime.now()
    rtc.set_time_and_date(current_system_time)  # Time and date may also be set as a tuple (hour, minute, second, year, month, date)
    while True:
        rtc_time = rtc.get_time_and_date()

        print(("The date is {0}/{1}/{2} at {3}:{4}:{5}").format(rtc_time.day, rtc_time.month, rtc_time.year, rtc_time.hour, rtc_time.minute, rtc_time.second))
        time.sleep(1)

except KeyboardInterrupt:
    pass
