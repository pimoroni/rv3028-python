#!/usr/bin/env python

import time

import rv3028

print("""get-time.py - Gets time and date from the RTC.

Press Ctrl+C to exit.

""")

# Create RV3028 instance
rtc = rv3028.RV3028()

# Switches RTC to backup battery if VCC goes below 2V
# Other settings: 'switchover_disabled', 'direct_switching_mode', 'standby_mode'
rtc.set_battery_switchover('level_switching_mode')

try:
    while True:
        rtc_time = rtc.get_time_and_date()
        print("The time is: {:02d}:{:02d}:{:02d} on :{:02d}/{:02d}/{:02d}".format(rtc_time.hour, rtc_time.minute, rtc_time.second, rtc_time.day, rtc_time.month, rtc_time.year))
        time.sleep(1)

except KeyboardInterrupt:
    pass
