#!/usr/bin/python
import time
from lib.kettle import Kettle
from yaml import load, dump
import threading
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

try:
    f = open('config.yaml')
    data = load(f, Loader=Loader)
    f.close()
except IOError:
    print "Error: Cannot find config file"
    exit(1)

#The list of kettles defined in the config file
kettles = {}
for config in data:
    kettles[config] =  Kettle(conf=data[config])
    kettles[config].start()
#Reads the config file  every five second and checks for changes. If changes are found it sets enabled and target for each kettle defined
while True:
    f = open('config.yaml','r')
    newdata = load(f, Loader=Loader)
    f.close()
    if data != newdata:
        print "reloading config"
        print data
        print newdata
        for config in newdata:
           kettles[config].setEnabled(newdata[config]["enabled"])
           kettles[config].setTarget(newdata[config]["target"])
    data = newdata
    time.sleep(5)
