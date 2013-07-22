import threading
import time
import datetime
import MySQLdb as mdb
from temp import Temp
from Adafruit_MCP230xx import *
class Kettle(threading.Thread):
    """
    A class for managing a brew kettle
    """

    def __init__(self, conf, name, brewid):
        threading.Thread.__init__(self)
        self.daemon = True
        if conf["enabled"] == "true":
            self.enabled = True
        else:
            self.enabled = False
        self.gpio_number = conf["gpio_number"]
        self.target = int(conf["target"])
        self.sensor = Temp(fileName = conf["temp_sensor"], correctionFactor = conf["temp_offset"])
        self.band = 0.2
        self.jee = Adafruit_MCP230XX(address=0x26, num_gpios=8, busnum=1)
        self.jee.config(self.gpio_number,self.jee.OUTPUT)
        self.name = name
        self.database = mdb.connect('chop.bad.wolf','brew','brewit','brewery')
        self.brewid = brewid

    def run(self):
        self.sensor.start()
        duty = 0
        while True:
            if self.isEnabled():
                self.sensor.setEnabled(True)
                currentTemp = self.sensor.getCurrentTemp()
                if currentTemp != -999:
                    self._updatedb(currentTemp)
                    if currentTemp < (self.target - 10):
                        duty = 100
                    elif (self.target - 5) < currentTemp < (self.target + self.band):
                        duty = 50
                    elif (self.target - 10) < currentTemp < (self.target - self.band):
                        duty = 75
                    else:
                        duty = 0
                if self.target > 299:
                    duty = self.target - 300
                print self.name + " is targetting " + str(self.target) + " and is at " + str(currentTemp) + " and " + str(duty) + "%"
                self._switch(duty)

            else:
                self.sensor.setEnabled(False)
            time.sleep(1)

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

    '''
    Takes the pin on a jeelabs output plug and sets it to 1 or 0 depending on if the heat should be on or not.
    '''
    def _switch(self, duty_cycle):
        self.jee.config(4,self.jee.OUTPUT)
        cycle_time = 2
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
            time = datetime.datetime.now()
            cursor = self.database.cursor()
            cursor.execute('INSERT INTO templog (brewid, time, temp, target, element) VALUES (%s,%s,%s,%s,%s)',(self.brewid, time, temp, self.target, self.name))
            self.database.commit()
            cursor.close()
        except:
            print "Error connecting to database"

        try:
            logfile = "/mnt/ramdisk/" + self.name
            with open (logfile, 'w+') as f: f.write(str(temp))
        except:
            print "Error writing to ramdisk file"
