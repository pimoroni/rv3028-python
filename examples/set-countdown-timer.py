#!/usr/bin/env python

import rv3028
import time

print("""set-countdown-timer.py - Set the periodic countdown timer to 5 x 1 second ticks and waits for alarm to be triggered.

Press Ctrl+C to exit.

""")

# Create RV3028 instance
rtc = rv3028.RV3028()

countdown_time = 5

try:
    rtc.stop_periodic_timer()
    rtc.set_periodic_timer_frequency('1Hz')  # Frequency of each timer tick can take '4036Hz', '63Hz','1Hz', '0.016Hz' (1Hz == 1 second)
    rtc.set_periodic_timer_countdown_value(countdown_time)  # Set number of timer ticks before countdown alarm is triggered
    rtc.clear_periodic_countdown_timer_interrupt()
    rtc.start_periodic_timer()  # Start timer running
    print('Countdown timer set for {} seconds\n'.format(countdown_time))
    while not rtc.get_periodic_countdown_timer_interrupt():
        print('Countdown is {}'.format(rtc.get_periodic_timer_countdown_status()))  # Show how many ticks are left of the countdown
        time.sleep(1)
    print('\nTimer alarm triggered!')

except KeyboardInterrupt:
    pass
