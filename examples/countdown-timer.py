#!/usr/bin/env python

import rv3028
import time

print("""set-time.py - Set the periodic coundown timer to 5 * 1 second ticks waits for alarm to be triggered
Press Ctrl+C to exit.

""")

rtc = rv3028.RV3028()

try:
    rtc.stop_periodic_timer()
    rtc.set_periodic_timer_frequency('1Hz')  # Frequency of each timer tick can take '4036Hz', '63Hz','1Hz', '0.016Hz'
    rtc.set_periodic_timer_countdown_value(5)  # Set number of timer ticks before countdown alarm is triggered
    rtc.clear_periodic_countdown_timer_interrupt()
    rtc.start_periodic_timer()  # Start timer running
    while not rtc.get_periodic_countdown_timer_interrupt():
        print('countdown is {0}'.format(rtc.get_periodic_timer_countdown_status()))  # show how many tick are left on the countdown
        time.sleep(0.5)
    print('Timer alarm triggered')

except KeyboardInterrupt:
    pass
