#!/usr/bin/python
import time
from lib.kettle import Kettle
from yaml import load, dump
import threading
import MySQLdb as mdb
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
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

#generates a new brewid if the database is connected.
def newbrewid(brewname):
    try:
        database = mdb.connect('chop.bad.wolf', 'brew', 'brewit', 'brewery');
        cursor = database.cursor()
        cursor.execute('INSERT INTO brewlog (brew) VALUES (%s)', [brewname])
        brewid = cursor.lastrowid
        database.commit()
        cursor.close()
    except:
        print "Error connecting to database, session will not be saved nor will the web interface work"
        brewid = 0
    return brewid


def start(brewname="adellewit", brewid=0):
    if brewid == 0:
        brewid = newbrewid(brewname)

    configfile="config.yaml"
    data = getconfig(configfile)
    if not data:
        exit(1)
#The list of kettles defined in the config file
    kettles = {}
    for config in data:
        kettles[config] = Kettle(conf=data[config], name=config, brewid=brewid)
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
        data = newdata
        time.sleep(5)


if __name__ == '__main__':
    start()
