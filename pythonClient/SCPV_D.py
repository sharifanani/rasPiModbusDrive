'''
This is a python library that hosts parameters and classes for the SCPV stepper
motor driver made by Clippard. It is part of the code being developped for
Immutrix Therapeutics.
The library is meant to run on a RaspberryPi 3 1GB SoC Computer, but can be
easily adapted to any device that runs python and has a python wrapper for its
GUI.
'''
#start by importing the RPIO and time libraries
import RPi.GPIO as RPIO
import time
#
# A class to be the base for a SCPV-D motor drivers
# arg: pins: list of pins used to with the driver.
#           The only pins used (for now) are
#           [DIR,STEP,ENABLE]
# var: position: holds the current motor position [0-100] = [closed - open]
# var: CONST_FULL_OPEN: maximum value for step range (fully open)
# var: CONST_FULL_CLOSE: minimum value for step range (fully closed)

#
class SCPV_D_t:
    def __init__(self,pins):
        self.pins = pins;
        assert type(self.pins) is list, "PINS IS NOT A LIST"
        assert(len(self.pins) == 3), "SCPV_D # pins != 3"
        self.__DIR_PIN = self.pins[0]
        self.__STEP_PIN = self.pins[1]
        self.__EN_PIN = self.pins[2]
        self.__PINS = {'DIR':self.pins[0],'STEP':self.pins[1],'EN':self.pins[2]}
        self.__MODES = {'IN':RPIO.IN, 'OUT':RPIO.OUT}
        self.pinMode('DIR','OUT')
        self.pinMode('STEP','OUT')
        self.pinMode('EN','OUT')
        self.position = 0;
        self.CONST_FULL_OPEN = 400
        self.CONST_FULL_CLOSE = 0

    # method: pinMode(self,pin,mode)
    # arg: pin: ['DIR','STEP','EN'] for direction, step, or enable pins
    # ard: mode:
    def pinMode(self,pin,mode):
        assert(mode in self.__MODES), "Invalid Mode"
        assert(pin in self.__PINS), "Unknown Pin"
        RPIO.setup(self.__PINS[pin],self.__MODES[mode])
        #todo: add support for pullups/pulldowns

    # method: setPin(self,pin,newVal): changes an attached pin to a new state
    # arg: pin: [DIR,STEP,EN] for direction, step, or enable pins
    # arg: newVal: boolean (True or False) corresponding to the state
    def setPin(self,pin,newVal):
        assert(type(newVal) is bool), "newVal should be True or False"
        assert(pin in self.__PINS), "Unknown Pin"
        if newVal:
            v=RPIO.HIGH
        else:
            v=RPIO.LOW
        RPIO.output(self.__PINS[pin],v)
        #todo: use the RPIO API to set the pins

    # method: getPin(self,pin): changes an attached pin to a new state
    # arg: pin: [DIR,STEP,EN] for direction, step, or enable pins
    # return: True or False corresponding to the state of the pin
    def getPin(self,pin):
        assert(pin in self.__PINS), "Unknown Pin"
        return RPIO.input(self.__PINS[pin])


    # method: movePosition(newPosition): moves the motor to the new position
    # arg: newPosition: new position integer [0-100] = [closed,open]
    def movePosition(self,newPosition):
        assert type(newPosition) is int, "New Position is not an integer"
        assert (newPosition>= 0 and newPosition <=100), "New position not in [0,100]"
        if(self.position == newPosition):
            return
        elif newPosition<self.position:
            self.setPin('DIR', True) #might need to be inverted
            numPulses = int((self.position-newPosition)*4)
            self.pulseOut('STEP',numPulses)

        elif newPosition>self.position:
            self.setPin('DIR', False) #might need to be inverted
            numPulses = int((-self.position+newPosition)*4)
            self.pulseOut('STEP',numPulses)
            #todo: pulse out the correct number of pulses
        else:
            pass
        self.position = newPosition

    # method: pulseOut(self,pin,numPulses):send out pulses on a pin
    # THIS METHOD SHALL NOT BE USED EXTERNALLY
    # arg: pin: pin to pulse out
    # arg: numPulses: number of pulses to send
    def pulseOut(self,pin,numPulses):
        count=0
        self.setPin('EN',True)
        #todo: find a better way that time.sleep to pulse out
        while count<numPulses:
            self.setPin(pin,not self.getPin(pin))
            time.sleep(0.005) #frequency set to 200Hz, 5ms per state
            count=count+1
        self.setPin('EN',False)
