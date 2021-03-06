import RPi.GPIO as GPIO
import time

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(0)
#p.start(2.5)

def loopServo():
    p.ChangeDutyCycle(5)
    time.sleep(0.5)
    p.ChangeDutyCycle(7.5)
    time.sleep(0.5)
    p.ChangeDutyCycle(10)
    time.sleep(0.5)
    p.ChangeDutyCycle(12.5)
    time.sleep(0.5)
    p.ChangeDutyCycle(10)
    time.sleep(0.5)
    p.ChangeDutyCycle(7.5)
    time.sleep(0.5)
    p.ChangeDutyCycle(5)
    time.sleep(0.5)
    p.ChangeDutyCycle(2.5)
    time.sleep(0.5)


def ringOnce():
    print("RING")
    p.ChangeDutyCycle(10)
    time.sleep(0.2)
    p.ChangeDutyCycle(2.5)
    time.sleep(3)


def testOnOffOn():
    print('starting')
    
    time.sleep(2)

    ringOnce()
    time.sleep(2)
    
    ringOnce()
    time.sleep(2)

    print('stopping')
    p.ChangeDutyCycle(0)
    time.sleep(2)
    

try:
    while True: 
        testOnOffOn()



finally:
    p.ChangeDutyCycle(2.5)
    p.stop()
    GPIO.cleanup()
