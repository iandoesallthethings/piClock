# -*- coding:utf-8 -*-
import SH1106
import time
import config
import traceback
import datetime
import subprocess
import humanize
from textwrap3 import wrap

import RPi.GPIO as GPIO


from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

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

# Clear display.
disp.clear()
# time.sleep(1)

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
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (disp.width, disp.height), "WHITE")

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('Font.ttf', 40)
font2 = ImageFont.truetype('Font.ttf', 16)
font10 = ImageFont.truetype('Font.ttf', 13)
fontTiny = ImageFont.truetype('Font.ttf', 11)
bell = Image.open("./bell.bmp").convert("1")
stopwatch = Image.open("./timer.bmp").convert("1")

# App State
refreshRate = 0.1 # in seconds

currentDisplay = 'timer'
alarmSet = True
timerRunning = True
timerStart = datetime.datetime.now()
timer = datetime.timedelta(seconds = 10)

# Input Handling
def setToClockMode(channel):
    print("Switching to Clock Mode")
    global currentDisplay
    currentDisplay = 'clock'

def setToTimerMode(channel):
    print("Switching to Timer Mode")
    global currentDisplay
    currentDisplay = 'timer'


def toggle(channel):
    if currentDisplay == 'clock':
        toggleAlarm()
    elif currentDisplay == 'timer':
        toggleTimer()

def toggleAlarm():
    print("Toggling Alarm")
    global alarmSet
    alarmSet = not alarmSet

def toggleTimer():
    global timerRunning, timerStart
    timerStart = datetime.datetime.now()
    timerRunning = not timerRunning

def up(channel):
    global timer
    timer += datetime.timedelta(minutes = 1)
def down(channel):
    global timer
    timer -= datetime.timedelta(minutes = 1)
def right(channel):
    global timer
    timer += datetime.timedelta(minutes = 5)
def left(channel):
    global timer
    timer -= datetime.timedelta(minutes = 5)

GPIO.add_event_detect(KEY1_PIN, GPIO.RISING, callback=setToClockMode)
GPIO.add_event_detect(KEY2_PIN, GPIO.RISING, callback=setToTimerMode)
GPIO.add_event_detect(KEY3_PIN, GPIO.RISING, callback=toggle)
GPIO.add_event_detect(KEY_UP_PIN, GPIO.RISING, callback=up)
GPIO.add_event_detect(KEY_DOWN_PIN, GPIO.RISING, callback=down)
GPIO.add_event_detect(KEY_LEFT_PIN, GPIO.RISING, callback=left)
GPIO.add_event_detect(KEY_RIGHT_PIN, GPIO.RISING, callback=right)


def displayClock(time):
    draw.text((0,-14), now.strftime("%I:%M"), font = font, fill = 0) # Time
    draw.text((98,16), now.strftime("%P"), font = fontTiny, fill = 0) # AM/PM
    draw.line([(30,40),(98,40)], fill = 0, width = 1) # Line
    draw.text((0,43), now.strftime("%a %d, %h %Y"), font = font2, fill = 0) # Date

def displayTimer(now):
    global timer, timerStart
    timeRemaining = None

    if timerRunning:
        timeElapsed = now - timerStart
        timeRemaining = timer - timeElapsed
        if timeRemaining <= datetime.timedelta(0):
            timeRemaining = datetime.timedelta(0)
    else:
        timeRemaining = timer

    for i, chunk in enumerate(formatTimerString(timeRemaining)):
        draw.text((10,15 * i), chunk, font = font10, fill = 0)

def formatTimerString(delta):
    preciseDelta = humanize.precisedelta(delta, minimum_unit = 'seconds')
    timeString = wrap(preciseDelta, width = 15)
    return timeString


# Program Loop
try:
    startTime = time.time()
    while True:
        draw.rectangle((0,0,disp.width,disp.height), fill=1) # Clear the frame
        
        if alarmSet == True:
            draw.bitmap((118,0), bell)
        if timerRunning == True:
            draw.bitmap((118,15), stopwatch)
            
        # Update the stuff
        now = datetime.datetime.now()

        # Display the stuff
        if currentDisplay == 'clock':
            displayClock(now)
        elif currentDisplay == 'timer':
            displayTimer(now)
        elif currentDisplay == 'derp':
            draw.text((10,0), 'DERP', font = font, fill = 0)

        # Update the display
        disp.ShowImage(disp.getbuffer(image))
        time.sleep(refreshRate - ((time.time() - startTime) % refreshRate))
finally:
    print("Cleaning Up")
    GPIO.cleanup()
