"""
Shamelessly stolen from
http://raspbrew.tumblr.com/post/44456213110/reading-temperatures-on-a-raspberry-pi-using-ds18b20
Thanks JohnSproull for putting this together
"""
from threading import Thread
import time


class Temp(Thread):
    """
     A class for getting the current temp of a DS18B20
    """

    def __init__(self, file_name, correction_factor=0):
        Thread.__init__(self)
        self.temp_dir = '/sys/bus/w1/devices/'
        self.file_name = file_name
        self.current_temp = -999
        self.correction_factor = correction_factor
        self.enabled = False
        self.daemon = True
    # if enabled, this reads the w1 file and
    # returns the temp, checking for crc.

    def run(self):
        while True:
            if self.is_enabled():
                try:
                    temp_file = self.temp_dir + self.file_name + "/w1_slave"
                    w1_slave = open(temp_file, 'r')
                except IOError:
                    print "Error: File " + temp_file + " does not exist."
                    time.sleep(30)
                    continue

                lines = w1_slave.readlines()
                crc_line = lines[0]
                temp_line = lines[1]
                result_list = temp_line.split("=")
                if crc_line.find("YES") > -1:
                    temp = float(result_list[-1])/1000  # temp in Celcius
                    temp = temp + self.correction_factor  # correction factor
                    temp = (9.0/5.0)*temp + 32
                    self.current_temp = temp
                else:
                    print "crc error on " + self.file_name
                w1_slave.close()
            time.sleep(1)

    def get_current_temp(self):
        '''returns the current temp for the probe'''
        return self.current_temp

    def set_enabled(self, enabled):
        '''setter to enable this probe'''
        self.enabled = enabled

    def is_enabled(self):
        '''getter to get the status of this probe'''
        return self.enabled
