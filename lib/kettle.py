import threading
import time
import datetime
from temp import Temp
from Adafruit_MCP230xx import *
import pidpy
class Kettle(threading.Thread):
    """
    A class for managing a brew kettle
    """

    def __init__(self, conf, name):
        threading.Thread.__init__(self)
        self.daemon = True
        if conf["enabled"] == "true":
            self.enabled = True
        else:
            self.enabled = False
        self.gpio_number = conf["gpio_number"]
        self.target = int(conf["target"])
        self.sensor = Temp(fileName = conf["temp_sensor"], correctionFactor = conf["temp_offset"])
        self.band = conf["band"]
        self.jee = Adafruit_MCP230XX(address=0x26, num_gpios=8, busnum=1)
        self.jee.config(self.gpio_number,self.jee.OUTPUT)
        self.name = name
        self.state = conf["state"]
        self.usePid = conf["usePid"]
        self.pid_K = conf["pid_K"]
        self.pid_I = conf["pid_I"]
        self.pid_D = conf["pid_D"]
        self.cycle_time = conf["cycle_time"]
        self.pid = pidpy.pidpy(self.cycle_time,self.pid_K,self.pid_I,self.pid_D)
    def run(self):
        self.sensor.start()
        duty = 0
        while True:
            if self.state == "control":
                self.sensor.setEnabled(True)
                currentTemp = self.sensor.getCurrentTemp()
                if currentTemp != -999:
                    self._updatedb(currentTemp)
                    duty = self.getDuty(currentTemp)
                print self.name + " is targetting " + str(self.target) + " and is at " + str(currentTemp) + " and " + str(duty) + "% on pin " + str(self.gpio_number)
                self._switch(duty)
            elif self.state == "monitor":
                self.sensor.setEnabled(True)
                currentTemp = self.sensor.getCurrentTemp()
                if currentTemp != 999:
                    self._updatedb(currentTemp)
                    time.sleep(2)
                print self.name + " is at " + str(currentTemp)
            else:
                self.sensor.setEnabled(False)
                self.jee.output(self.gpio_number,0)

    def getDuty(self, currentTemp):
        duty = 0
        #return manual duty
        if self.target > 299:
            return self.target - 300
        #if no temp is given, turn it off.
        if currentTemp == -999:
            return 0
        #insert pid logics here
        if self.usePid:
            duty = self.pid.calcPID_reg4(currentTemp, self.target)
            print duty
            return duty
        #simple on/off logic
        else:
            if currentTemp < (self.target - 10):
                duty = 100
            elif (self.target - 5) < currentTemp < (self.target + self.band):
                duty = 50
            elif (self.target - 10) < currentTemp < (self.target - self.band):
                duty = 75
            else:
                duty = 0
            return duty



    def getTarget(self):
        return self.target

    def setTarget(self, target):
        self.target = int(target)

    def setEnabled(self, enabled):
        if enabled == "true":
            self.enabled = True
        else:
            self.enabled = False

    def isEnabled(self):
        return self.enabled

    def setState(self, state):
        if (state == "disabled") or (state == "monitor") or (state == "control"):
            self.state = state
        else:
            print "invalid state configured, setting state to disabled"
            self.state = "disabled"
    def getState(self):
        return self.state

    def setConfig(self, conf):
        if conf["enabled"] == "true":
            self.enabled = True
        else:
            self.enabled = False
        self.target = int(conf["target"])
        self.band = conf["band"]
        self.state = conf["state"]
        self.usePid = conf["usePid"]
        self.pid_K = conf["pid_K"]
        self.pid_I = conf["pid_I"]
        self.pid_D = conf["pid_D"]
        self.cycle_time = conf["cycle_time"]

        '''
    Takes the pin on a jeelabs output plug and sets it to 1 or 0 depending on if the heat should be on or not.
    '''
    def _switch(self, duty_cycle):
        self.jee.config(self.gpio_number,self.jee.OUTPUT)
        cycle_time = self.cycle_time
        if duty_cycle == 100:
            self.jee.output(self.gpio_number,1)
            time.sleep(cycle_time)
        elif duty_cycle == 0:
            self.jee.output(self.gpio_number,0)
            time.sleep(cycle_time)
        else:
            duty = duty_cycle/100.0
            self.jee.output(self.gpio_number,1)
            time.sleep(cycle_time*(duty))
            self.jee.output(self.gpio_number,0)
            time.sleep(cycle_time*(1.0-duty))
        return

    '''
    takes the temperature and updates the database as well as the ramdisk file
    '''
    def _updatedb(self, temp):
        try:
            logfile = "/mnt/ramdisk/" + self.name
            with open (logfile, 'w+') as f: f.write(str(temp))
        except:
            print "Error writing to ramdisk file"
