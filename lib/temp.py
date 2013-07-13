"""
Shamelessly stolen from http://raspbrew.tumblr.com/post/44456213110/reading-temperatures-on-a-raspberry-pi-using-ds18b20
Thanks JohnSproull for putting this together
"""
from threading import Thread
import time

class Temp(Thread):
    """
     A class for getting the current temp of a DS18B20
    """

    def __init__(self, fileName, correctionFactor=0):
        Thread.__init__(self)
        self.tempDir = '/sys/bus/w1/devices/'
        self.fileName = fileName
        self.currentTemp = -999
        self.correctionFactor = correctionFactor;
        self.enabled = False
        self.daemon = True
    # if enabled, this reads the w1 file and returns the temp, checking for crc.
    def run(self):
        while True:
            if self.isEnabled():
                try:
                    f = open(self.tempDir + self.fileName + "/w1_slave", 'r')
                except IOError as e:
                    print "Error: File " + self.tempDir + self.fileName + "/w1_slave" + " does not exist.";
                    return;

                lines=f.readlines()
                crcLine=lines[0]
                tempLine=lines[1]
                result_list = tempLine.split("=")
                if crcLine.find("YES") > -1:
                    temp = float(result_list[-1])/1000 # temp in Celcius
                    temp = temp + self.correctionFactor # correction factor
                    temp = (9.0/5.0)*temp + 32
                    self.currentTemp = temp
                else:
                    print "crc error on " + self.fileName
                #print "Current: " + str(self.currentTemp) + " " + str(self.fileName)

            time.sleep(1)

    #returns the current temp for the probe
    def getCurrentTemp(self):
        return self.currentTemp

    #setter to enable this probe
    def setEnabled(self, enabled):
        self.enabled = enabled
    #getter
    def isEnabled(self):
        return self.enabled
