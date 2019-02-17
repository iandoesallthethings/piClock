import board
import busio
import adafruit_ds3231
import time

from board import *

i2c = busio.I2C(SCL,SDA)
rtc = adafruit_ds3231.DS3231(i2c)

print(rtc.datetime)

rtc.datetime = time.struct_time((2021, 1, 15, 18, 8, 0, 6, 1, -1))

print(rtc.datetime)
