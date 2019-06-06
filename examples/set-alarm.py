#!/usr/bin/env python

import rv3028
import time

print("""set-time.py - Sets alarm for 5 seconds time when the minute changes and waits for alarm to be triggered
Press Ctrl+C to exit.

""")

rtc = rv3028.RV3028()

try:

    rtc.set_time((1, 1, 55))  # time set using tuple (hour, minute, second)
    rtc_time = rtc.get_time_and_date()
    print(("The date is {0}/{1}/{2} at {3}:{4}:{5}").format(rtc_time.day, rtc_time.month, rtc_time.year, rtc_time.hour, rtc_time.minute, rtc_time.second))
    alarm_time = rtc.get_time_and_date()
    alarm_time = alarm_time.replace(minute=2)
    print(("Alarm date is {0}/{1}/{2} at {3}:{4}:{5}").format(alarm_time.day, alarm_time.month, alarm_time.year, alarm_time.hour, alarm_time.minute, alarm_time.second))
    rtc.set_alarm_time(alarm_time, weekday=0)  # Set weekday to 1 if requiring a weekly alarm interval set alarm can also take a tuple (weekday/date, hour, minute)

    '''
    Set alarm frequency valid entrys 'disabled_weekly', 'disabled_monthly', 'hourly_on_minute','daily_on_hour', 'daily_on_hour_and_minute', 'weekly',
        'weekly_on_minute''weekly_on_hour', 'weekly_on_hour_and_minute', 'monthly', 'monthly_on_minute', 'monthly_on_hour', 'monthly_on_hour_and_minute'
    '''
    rtc.set_alarm_setting('hourly_on_minute')
    rtc.clear_alarm_interrupt()

    while not rtc.get_alarm_interrupt():
        print ('Waiting for alarm')
        time.sleep(0.5)

    rtc_time = rtc.get_time_and_date()
    print(("Alarm triggered on {0}/{1}/{2} at {3}:{4}:{5}").format(rtc_time.day, rtc_time.month, rtc_time.year, rtc_time.hour, rtc_time.minute, rtc_time.second))

except KeyboardInterrupt:
    pass
