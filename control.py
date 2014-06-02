#!/usr/bin/python
import time
from lib.kettle import Kettle
from yaml import load, dump
import threading
import MySQLdb as mdb
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print("not loading cloader")
    from yaml import Loader, Dumper

#returns the configuration dictionary from a yaml file
def getconfig(file):
    try:
        f = open(file)
        data = load(f, Loader=Loader)
        f.close
        return data
    except IOError:
        print "Error: Cannot find config file " + file
        return 0

def start():
    configfile="/home/jkeppers/drunken-control/config.yaml"
    data = getconfig(configfile)
    if not data:
        exit(1)
#The list of kettles defined in the config file
    kettles = {}
    for config in data:
        kettles[config] = Kettle(conf=data[config], name=config)
        kettles[config].start()
#Reads the config file  every five second and checks for changes. If changes are found it sets enabled and target for each kettle defined
    while True:
        newdata = getconfig(configfile)
        if not newdata:
            time.sleep(2)
            continue
        if data != newdata:
            print "reloading config"
            for config in newdata:
               kettles[config].setEnabled(newdata[config]["enabled"])
               kettles[config].setTarget(newdata[config]["target"])
               kettles[config].setState(newdata[config]["state"])
               kettles[config].setConfig(newdata[config])
        data = newdata
        time.sleep(5)


if __name__ == '__main__':
    start()
