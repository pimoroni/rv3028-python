#!/usr/bin/env python

import rv3028
import time
import datetime

print("""set-time.py - Sets alarm for 5 minutes time, recurring hourly,
and waits for alarm to be triggered.

Press Ctrl+C to exit.

""")

# Create RV3028 instance
rtc = rv3028.RV3028()

try:
    rtc.clear_alarm_interrupt()
    current_system_time = datetime.datetime.now()
    rtc.set_time_and_date(current_system_time)  # Set time to current system time
    rtc_time = rtc.get_time_and_date()

    print("The time is: {:02d}:{:02d}:{:02d} on :{:02d}/{:02d}/{:02d}".format(rtc_time.hour, rtc_time.minute, rtc_time.second, rtc_time.day, rtc_time.month, rtc_time.year))

    # Set alarm for 5 minutes time
    alarm_minutes = 5
    alarm_time = rtc_time + datetime.timedelta(minutes=alarm_minutes)
    rtc.set_alarm_time(alarm_time)

    print("Alarm set for: {:02d}:{:02d}:{:02d} on: {:02d}/{:02d}/{:02d}\n".format(alarm_time.hour, alarm_time.minute, alarm_time.second, alarm_time.day, alarm_time.month, alarm_time.year))

    # Valid alarm frequencies: 'disabled_weekly', 'disabled_monthly', 'hourly_on_minute','daily_on_hour', 'daily_on_hour_and_minute', 'weekly',
    # 'weekly_on_minute', 'weekly_on_hour', 'weekly_on_hour_and_minute', 'monthly', 'monthly_on_minute', 'monthly_on_hour', 'monthly_on_hour_and_minute'

    # This alarm will recur hourly
    rtc.set_alarm_setting("hourly_on_minute")

    print(rtc.get_alarm_time())

    # Poll for alarm interrupt
    while not rtc.get_alarm_interrupt():
        print("Waiting for alarm...")
        time.sleep(1)

    rtc_time = rtc.get_time_and_date()
    print("\nAlarm triggered at: {:02d}:{:02d}:{:02d} on: {:02d}/{:02d}/{:02d}!".format(rtc_time.hour, rtc_time.minute, rtc_time.second, rtc_time.day, rtc_time.month, rtc_time.year))

except KeyboardInterrupt:
    pass
