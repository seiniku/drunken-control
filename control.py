#!/usr/bin/python
'''main control file'''
import time
from lib.kettle import Kettle
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    print "not loading cloader"
    from yaml import Loader


def get_config(conf_file):
    '''returns the configuration dictionary from a yaml file'''
    try:
        with open(conf_file) as config:
            # config = open(conf_file)
            data = load(config, Loader=Loader)
            # config.close
            return data
    except IOError:
        print "Error: Cannot find config file " + conf_file
        return 0


def start():
    '''main logic loop'''
    configfile = "/home/jkeppers/drunken-control/config.yaml"
    data = get_config(configfile)
    if not data:
        exit(1)
    # The list of kettles defined in the config file
    kettles = {}
    for config in data:
        kettles[config] = Kettle(conf=data[config], name=config)
        kettles[config].start()
    # Reads the config file  every five second and checks for changes.
    # If changes are found it sets enabled and target for each kettle defined
    while True:
        newdata = get_config(configfile)
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
