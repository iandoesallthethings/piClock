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
import pickle


# Setup
refreshRate = 0.1 # in seconds
bouncetime = 100 # in milliseconds

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

SERVO_PIN      = 4



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
GPIO.setup(SERVO_PIN, GPIO.OUT) # Output for PWM servo signal

servo = GPIO.PWM(SERVO_PIN, 50) # PWM signal at 50Hz
servo.start(0)
# servo.start(3) # Start the servo at 2.5% duty cycle.

def showClock(_):
    global view
    view = Clock

def showTimer(_):
    global view
    view = Timer

GPIO.add_event_detect(KEY1_PIN, GPIO.RISING, callback=showClock, bouncetime=bouncetime)
GPIO.add_event_detect(KEY2_PIN, GPIO.RISING, callback=showTimer, bouncetime=bouncetime)
GPIO.add_event_detect(KEY3_PIN, GPIO.RISING, callback=lambda _: view.toggle(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_UP_PIN, GPIO.RISING, callback=lambda _: view.up(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_DOWN_PIN, GPIO.RISING, callback=lambda _: view.down(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_LEFT_PIN, GPIO.RISING, callback=lambda _: view.left(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_RIGHT_PIN, GPIO.RISING, callback=lambda _: view.right(), bouncetime=bouncetime)
GPIO.add_event_detect(KEY_PRESS_PIN, GPIO.RISING, callback=lambda _: view.click(), bouncetime=bouncetime)


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

# Servo Control

# Helpers
def chopMicroseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)

def humanizeAndWrapTime(delta):
    delta = chopMicroseconds(delta)
    preciseDelta = humanize.precisedelta(delta, minimum_unit = 'seconds')
    timeString = wrap(preciseDelta, width = 12)
    return timeString

def addDeltaToTime(time, delta):
    temp_datetime = datetime.datetime.combine(datetime.date.today(), time)
    sum = temp_datetime + delta
    return sum.time()

def subtractDeltaFromTime(time, delta):
    temp_datetime = datetime.datetime.combine(datetime.date.today(), time)
    sum = temp_datetime - delta
    return sum.time()

# Views
class Alarm:
    ringing = False
        
    def on():
        global servo
        Alarm.ringing = True
        servo.ChangeDutyCycle(2.5)
    def off():
        global servo
        Alarm.ringing = False
        servo.ChangeDutyCycle(2.5)
        time.sleep(0.2)
        servo.ChangeDutyCycle(0)
    def ringOnce():
        global servo
        servo.ChangeDutyCycle(10)
        time.sleep(0.2)
        servo.ChangeDutyCycle(2.5)


class Clock:
    alarmSet = False
    alarmTime = datetime.time(hour = 9, minute = 0)
    alarmRinging = False
    editingAlarm = False
    editDeltas = [datetime.timedelta(hours = 1), datetime.timedelta(minutes = 1)]
    editing = 0

    ringInterval = 1 # in seconds
    ringTimer = 0

    def draw():
        draw.text((0,-14), now.strftime("%I:%M"), font = font, fill = 0) # Time
        draw.text((98,16), now.strftime("%P"), font = fontTiny, fill = 0) # AM/PM
        draw.line([(30,40),(98,40)], fill = 0, width = 1) # Line
        if Clock.editingAlarm: 
            draw.text((0,43), Clock.alarmTime.strftime("%I:%M %P"), font = font2, fill = 0) # Alarm
            draw.line([(0 + (Clock.editing * 20),63),(20 + (Clock.editing * 20),63)], fill = 0, width = 1) # Underline
        else: 
            draw.text((0,43), now.strftime("%a %d, %h %Y"), font = font2, fill = 0) # Date

    def click():
        Clock.editingAlarm = not Clock.editingAlarm
    def up():
        Clock.alarmTime = addDeltaToTime(Clock.alarmTime, Clock.editDeltas[Clock.editing])
    def down():
        Clock.alarmTime = subtractDeltaFromTime(Clock.alarmTime, Clock.editDeltas[Clock.editing])
    def left():
        Clock.editing = 0
    def right():
        Clock.editing = 1

    def toggle():
        Clock.alarmSet = not Clock.alarmSet
        Clock.alarmRinging = False
        Alarm.off()


    def checkAlarm():
        global view
        if now.time().replace(microsecond=0) == Clock.alarmTime and Clock.alarmSet:
            view = Clock
            Clock.alarmRinging = True
            Alarm.on()

    def ringAlarm():
        global refreshRate
        if Clock.ringTimer == 0: 
            Alarm.ringOnce()
        Clock.ringTimer += refreshRate
        if Clock.ringTimer >= Clock.ringInterval: Clock.ringTimer = 0


class Timer:
    duration = datetime.timedelta(minutes = 5)
    start = datetime.datetime.now()
    running = False
    ringing = False

    ringInterval = 2 # in seconds
    ringTimer = 0 # increments by refreshrate
    
    def draw():
        humanizedTime = humanizeAndWrapTime(Timer.timeRemaining())
        for i, chunk in enumerate(humanizedTime):
            draw.text((10,15 * i), chunk, font = font10, fill = 0)

    def up():
        Timer.duration += datetime.timedelta(minutes = 1)
    def down():
        Timer.duration -= datetime.timedelta(minutes = 1)
    def right():
        Timer.duration += datetime.timedelta(minutes = 5)
    def left():
        Timer.duration -= datetime.timedelta(minutes = 5)

    def toggle():
        Timer.start = datetime.datetime.now()
        Timer.running = not Timer.running
        Timer.ringing = False
        Alarm.off()


    def check():
        global view
        if Timer.running and Timer.timeRemaining() <= datetime.timedelta(0) and Timer.ringing == False:
            Timer.ringing = True
            view = Timer
            Alarm.on()
    def ring():
        global refreshRate
        if Timer.ringTimer <= 0: 
            Alarm.ringOnce()
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

def saveSettings():
    with open('settings.txt', 'wb') as f:
        pickle.dump([ Clock.alarmSet, Clock.alarmTime, Timer.duration, Timer.running, Timer.start ], f)

def loadSettings():   
    with open('settings.txt', 'rb') as f:
         Clock.alarmSet, Clock.alarmTime, Timer.duration, Timer.running, Timer.start = pickle.load(f)

# Main
try:
    startTime = time.time()
    view = Clock
    loadSettings()
    while True:
        now = datetime.datetime.now()
                
        draw.rectangle((0,0,disp.width,disp.height), fill=1) # Clear the frame
        
        if Clock.alarmSet: draw.bitmap((118,0), bell)
        if Timer.running: draw.bitmap((118,15), stopwatch)

        Clock.checkAlarm()
        if Clock.alarmRinging: Clock.ringAlarm()

        Timer.check()
        if Timer.ringing: Timer.ring()

        if now.second % 30 == 0 and now.microsecond <= 200000:
            saveSettings()

        # Display the stuff
        view.draw()

        # Update the display
        disp.ShowImage(disp.getbuffer(image))
        time.sleep(refreshRate - ((time.time() - startTime) % refreshRate))
finally:
    print("Cleaning Up")
    servo.stop()
    GPIO.cleanup()
    print("Done!")
