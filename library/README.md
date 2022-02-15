# RV3028 Real Time Clock Breakout

[![Build Status](https://shields.io/github/workflow/status/pimoroni/rv3028-python/Python%20Tests.svg)](https://github.com/pimoroni/rv3028-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/rv3028-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/rv3028-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/rv3028.svg)](https://pypi.python.org/pypi/rv3028)
[![Python Versions](https://img.shields.io/pypi/pyversions/rv3028.svg)](https://pypi.python.org/pypi/rv3028)

# Note

This is just a Python library to interface with the RV3028 and does not install the RTC as a time source for Raspbian.

In order to set up as a RTC in Raspbian you will need to add something like the following to `/boot/config.txt`:

```
dtoverlay=i2c-rtc,rv3028,backup-switchover-mode=1
```

More information is available in the `i2c-rtc` dtoverlay documentation: https://github.com/raspberrypi/linux/blob/0d72d83ec92acda1e8cbad0d4213a5ec2b3f2e1b/arch/arm/boot/dts/overlays/README#L1079

# Installing

Stable library from PyPi:

* Just run `python3 -m pip install rv3028`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/rv3028-python`
* `cd rv3028-python`
* `sudo ./install.sh --unstable`

# Requirements

This library depends upon smbus:

```
sudo apt install python-smbus   # Python 2
sudo apt install python3-smbus  # Python 3
```


# Changelog
0.0.5
-----

* Bugfix: corrected BCD month to include Oct, Nov, Dec

0.0.4
-----

* Port to i2cdevice>=0.0.6 set/get API
* Cleaned up i2cdevice bindings
* Corrected 12-hour and am/pm bits in bindings

0.0.3
-----

* Bugfix to support days of month in the 20s

0.0.2
-----

* Major bugfix to support hours past 8PM
* Other minor fixes and improvements

0.0.1
-----

* Initial Release
