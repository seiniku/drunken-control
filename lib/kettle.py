""" This module defines a kettle and it's state """
import traceback
import threading
import time
from lib.temp import Temp
from lib.Adafruit_MCP230xx import Adafruit_MCP230XX
from lib.mypid import mypid
import graphitesend


class Kettle(threading.Thread):
    """
    A class for managing a brew kettle
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, conf, name):
        threading.Thread.__init__(self)
        self.daemon = True
        if conf["enabled"] == "true":
            self.enabled = True
        else:
            self.enabled = False
        self.gpio_number = conf["gpio_number"]
        self.target = int(conf["target"])
        self.sensor = Temp(fileName=conf["temp_sensor"],
                           correctionFactor=conf["temp_offset"])
        self.band = conf["band"]
        self.jee = Adafruit_MCP230XX(address=0x26, num_gpios=8, busnum=1)
        self.jee.config(self.gpio_number, self.jee.OUTPUT)
        self.name = name
        self.state = conf["state"]
        self.use_pid = conf["use_pid"]
        self.pid_kp = conf["pid_Kc"]
        self.pid_ki = conf["pid_Ti"]
        self.pid_kd = conf["pid_Td"]
        self.cycle_time = conf["cycle_time"]
        self.pid = mypid(kp=self.pid_kp,
                         ki=self.pid_ki,
                         kd=self.pid_kd,
                         history_depth=3)

    def run(self):
        """
        The main logic
        """
        self.sensor.start()
        duty = 0
        while True:
            if self.state == "control":
                self.sensor.set_enabled(True)
                current_temp = self.sensor.get_current_temp()
                if current_temp != -999:
                    duty = self.get_duty(current_temp)
                    self._updatedb(current_temp, duty)
                self._switch(duty)
            elif self.state == "monitor":
                self.sensor.set_enabled(True)
                current_temp = self.sensor.get_current_temp()
                if current_temp != 999:
                    self._updatedb(current_temp, duty)
                    time.sleep(2)
                # print self.name + " is at " + str(current_temp)
            else:
                self.sensor.set_enabled(False)
                self.jee.output(self.gpio_number, 0)

    def get_duty(self, current_temp):
        """
        This figures out what the duty cycle should be for the element
        """
        duty = 0
        # return manual duty
        if self.target > 299:
            return self.target - 300
        # if no temp is given, turn it off.
        if current_temp == -999:
            return 0
        # insert pid logics here
        if self.use_pid:
            duty = self.pid.get_duty(current_temp, self.target)
            return duty
        # simple on/off logic
        else:
            if current_temp < (self.target - 10):
                duty = 100
            elif (self.target - 5) < current_temp < (self.target + self.band):
                duty = 50
            elif (self.target - 10) < current_temp < (self.target - self.band):
                duty = 75
            else:
                duty = 0
            return duty

    def get_target(self):
        """ Returns the target temperature """
        return self.target

    def set_target(self, target):
        """ Sets the target temperature """
        self.target = int(target)

    def set_enabled(self, enabled):
        """ Sets if kettle is enabled """
        if enabled == "true":
            self.enabled = True
        else:
            self.enabled = False

    def is_enabled(self):
        """ Checks if kettle is enabled """
        return self.enabled

    def set_state(self, state):
        """ Sets the kettle state """
        if state in ["disabled", "monitor", "control"]:
            self.state = state
        else:
            print "invalid state configured, setting state to disabled"
            self.state = "disabled"

    def get_state(self):
        """ Returns the kettle state """
        return self.state

    def set_config(self, conf):
        """ Builds the kettle config """
        if conf["enabled"] == "true":
            self.enabled = True
        else:
            self.enabled = False
        self.target = int(conf["target"])
        self.band = conf["band"]
        self.state = conf["state"]
        self.use_pid = conf["use_pid"]
        self.pid_kp = conf["pid_Kc"]
        self.pid_ki = conf["pid_Ti"]
        self.pid_kd = conf["pid_Td"]
        self.cycle_time = conf["cycle_time"]

        self.pid = mypid(kp=self.pid_kp,
                         ki=self.pid_ki,
                         kd=self.pid_kd,
                         history_depth=3)

    def _switch(self, duty_cycle):
        '''
        Takes the pin on a jeelabs output plug and sets it to 1 or 0
        depending on if the heat should be on or not.
        '''
        self.jee.config(self.gpio_number, self.jee.OUTPUT)
        cycle_time = self.cycle_time
        if duty_cycle == 100:
            self.jee.output(self.gpio_number, 1)
            time.sleep(cycle_time)
        elif duty_cycle == 0:
            self.jee.output(self.gpio_number, 0)
            time.sleep(cycle_time)
        else:
            duty = duty_cycle/100.0
            self.jee.output(self.gpio_number, 1)
            time.sleep(cycle_time*(duty))
            self.jee.output(self.gpio_number, 0)
            time.sleep(cycle_time*(1.0-duty))
        return

    def _updatedb(self, temp, duty):
        '''
        takes the temperature and updates the database
        as well as the ramdisk file
        '''
        try:
            logfile = "/mnt/ramdisk/" + self.name
            with open(logfile, 'w+') as ram_file:
                ram_file.write(str(temp))
        except IOError:
            print "Error writing to ramdisk file"
        # send to graphite
        if self.state == "control":
            target = self.target
        else:
            target = 0
        summary = {'temperature': temp, 'target': target, 'duty': duty}

        try:
            graph = graphitesend.init(graphite_server='192.168.1.3',
                                      prefix="brewing",
                                      system_name=self.name)
            graph.send_dict(summary)
        except:
            print "error sending to graphite"
            traceback.print_exc()
