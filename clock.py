# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import SH1106
import config
import traceback

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import time
import datetime
import humanize
from textwrap3 import wrap


#GPIO define
RST_PIN        = 25
CS_PIN         = 8
DC_PIN         = 24

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13

KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16


# 240x240 display with hardware SPI:
disp = SH1106.SH1106()
disp.Init()


#init GPIO
# for P4:
# sudo vi /boot/config.txt
# gpio=6,19,5,26,13,21,20,16=pu
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# Clear display.
disp.clear()

# Create blank image for drawing with mode '1' for 1-bit color.
image = Image.new('1', (disp.width, disp.height), "WHITE")

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('Font.ttf', 40)
font2 = ImageFont.truetype('Font.ttf', 16)
font10 = ImageFont.truetype('Font.ttf', 13)
fontTiny = ImageFont.truetype('Font.ttf', 11)
# Import BMPs
bell = Image.open("./bell.bmp").convert("1")
stopwatch = Image.open("./timer.bmp").convert("1")

# Helpers
def showClock(_):
    global view
    view = Clock

def showTimer(_):
    global view
    view = Timer

def chopMicroseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)

def humanizeAndWrapTime(delta):
    delta = chopMicroseconds(delta)
    preciseDelta = humanize.precisedelta(delta, minimum_unit = 'seconds')
    timeString = wrap(preciseDelta, width = 12)
    return timeString

# Views
class Clock:
    alarmSet = False
    alarmTime = datetime.time(hour = 15, minute = 27)
    alarmRinging = False

    ringInterval = 1 # in seconds
    ringTimer = 0

    def draw():
        draw.text((0,-14), now.strftime("%I:%M"), font = font, fill = 0) # Time
        draw.text((98,16), now.strftime("%P"), font = fontTiny, fill = 0) # AM/PM
        draw.line([(30,40),(98,40)], fill = 0, width = 1) # Line
        #draw.text((0,43), now.strftime("%a %d, %h %Y"), font = font2, fill = 0) # Date
        draw.text((0,43), Clock.alarmTime.strftime("%I:%M %P"), font = font2, fill = 0) # Date

    def toggle():
        Clock.alarmSet = not Clock.alarmSet
        Clock.alarmRinging = False

    def up():
        print('clock up')
    def down():
        print('clock down')
    def right():
        print('clock right')
    def left():
        print('clock left')

    def checkAlarm():
        if now.time().replace(microsecond=0) == Clock.alarmTime and Clock.AlarmSet:
            Clock.alarmRinging = True

    def ringAlarm():
        global refreshRate
        if Clock.ringTimer == 0: print("RING! WAKE UP!") # Ring the actual bell HERE!
        Clock.ringTimer += refreshRate
        if Clock.ringTimer >= Clock.ringInterval: Clock.ringTimer = 0

class Timer:
    duration = datetime.timedelta(seconds = 10)
    start = datetime.datetime.now()
    running = False
    ringing = False

    ringInterval = 2 # in seconds
    ringTimer = 0 # increments by refreshrate
    

    def check():
        if Timer.running and Timer.timeRemaining() <= datetime.timedelta(0):
            Timer.ringing = True
    def ring():
        global refreshRate
        if Timer.ringTimer <= 0: print("RING! TIMES UP!") # Ring the actual bell HERE!
        Timer.ringTimer += refreshRate
        if Timer.ringTimer >= Timer.ringInterval: Timer.ringTimer = 0


    def timeRemaining():
        timeRemaining = None
        if Timer.running:
            timeElapsed = now - Timer.start
            timeRemaining = Timer.duration - timeElapsed
        else:
            timeRemaining = Timer.duration
        if timeRemaining <= datetime.timedelta(0):
            timeRemaining = datetime.timedelta(0)
        return timeRemaining
    
    def draw():
        humanizedTime = humanizeAndWrapTime(Timer.timeRemaining())
        for i, chunk in enumerate(humanizedTime):
            draw.text((10,15 * i), chunk, font = font10, fill = 0)

    def toggle():
        Timer.start = datetime.datetime.now()
        Timer.running = not Timer.running
        Timer.ringing = False

    def up():
        Timer.duration += datetime.timedelta(minutes = 1)
    def down():
        Timer.duration -= datetime.timedelta(minutes = 1)
    def right():
        Timer.duration += datetime.timedelta(minutes = 5)
    def left():
        Timer.duration -= datetime.timedelta(minutes = 5)

# Setup
refreshRate = 0.1 # in seconds
bouncetime = 100 # in milliseconds
view = Clock

GPIO.add_event_detect(KEY1_PIN, GPIO.RISING, callback=showClock, bouncetime=bouncetime)
GPIO.add_event_detect(KEY2_PIN, GPIO.RISING, callback=showTimer, bouncetime=bouncetime)
GPIO.add_event_detect(KEY3_PIN, GPIO.RISING, callback=lambda _: view.toggle(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_UP_PIN, GPIO.RISING, callback=lambda _: view.up(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_DOWN_PIN, GPIO.RISING, callback=lambda _: view.down(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_LEFT_PIN, GPIO.RISING, callback=lambda _: view.left(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_RIGHT_PIN, GPIO.RISING, callback=lambda _: view.right(), bouncetime=bouncetime)

# Main
try:
    startTime = time.time()
    while True:
        now = datetime.datetime.now()
                
        draw.rectangle((0,0,disp.width,disp.height), fill=1) # Clear the frame
        
        if Clock.alarmSet: draw.bitmap((118,0), bell)
        if Timer.running: draw.bitmap((118,15), stopwatch)

        Clock.checkAlarm()
        if Clock.alarmRinging: Clock.ringAlarm()

        Timer.check()
        if Timer.ringing: Timer.ring()


        # Display the stuff
        view.draw()

        # Update the display
        disp.ShowImage(disp.getbuffer(image))
        time.sleep(refreshRate - ((time.time() - startTime) % refreshRate))
finally:
    print("Cleaning Up")
    GPIO.cleanup()
