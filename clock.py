# -*- coding:utf-8 -*-
import SH1106
import time
import config
import traceback
import datetime

import RPi.GPIO as GPIO

import time
import subprocess

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

# App State
currentDisplay = 'clock'
alarmSet = True

# Input Handling
def setToClockMode(channel):
    global currentDisplay
    currentDisplay = 'clock'

def setToTimerMode(channel):
    global currentDisplay
    currentDisplay = 'timer'

def setToDerpMode(channel):
    global currentDisplay
    currentDisplay = 'derp'

def toggleAlarm(channel):
    global alarmSet
    alarmSet = not alarmSet

GPIO.add_event_detect(KEY1_PIN, GPIO.RISING, callback=setToClockMode)
GPIO.add_event_detect(KEY2_PIN, GPIO.RISING, callback=toggleAlarm)
GPIO.add_event_detect(KEY3_PIN, GPIO.RISING, callback=setToDerpMode)

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

def displayClock(time):
    draw.text((0,-14), now.strftime("%I:%M"), font = font, fill = 0)
    draw.text((98,16), now.strftime("%P"), font = fontTiny, fill = 0)
    draw.line([(30,40),(98,40)], fill = 0, width = 1)
    draw.text((0,43), now.strftime("%a %d, %h %Y"), font = font2, fill = 0)
    draw.bitmap((117,0), bell)

# Program Loop
startTime = time.time()
while True:
    draw.rectangle((0,0,disp.width,disp.height), fill=1) # Clear the frame

    now = datetime.datetime.now()
    if currentDisplay == 'clock':
        displayClock(now)
        time.sleep(1.0 - ((time.time() - startTime) % 1))
    elif currentDisplay == 'timer':
        draw.text((10,0), 'This is where the timer goes', font = font10, fill = 0)
    elif currentDisplay == 'derp':
        draw.text((10,0), 'DERP', font = font, fill = 0)

    disp.ShowImage(disp.getbuffer(image))
    
# except:
	# print("except")
# GPIO.cleanup()
