import RPi.GPIO as RPIO

import time

RPIO.setmode(RPIO.BOARD)

RPIO.setup(40,RPIO.OUT)
while True:
    RPIO.output(40,True)
    time.sleep(0.5)
    RPIO.output(40,False)
    time.sleep(0.5)
