#!/usr/bin/python
import sys, time
from smbus import SMBus
import datetime
from Adafruit_MCP230xx import *
import MySQLdb as mdb
'''
Takes the pin on a jeelabs output plug and sets it to 1 or 0 depending on if the heat should be on or not.
'''
def switch(jee,pin,duty_cycle):
    cycle_time = 2
    if duty_cycle == 100:
        jee.output(pin,1)
        time.sleep(cycle_time)
    elif duty_cycle == 0:
        jee.output(pin,0)
        time.sleep(cycle_time)
    else:
        duty = duty_cycle/100.0
        #on for xtime
        jee.output(pin,1)
	print "on"
        time.sleep(cycle_time*(duty))
        #off for ytime
        jee.output(pin,0)
	print "off"
        time.sleep(cycle_time*(1.0-duty))
    return

# returns temperature of the 1wire sensor. Needs to be abstracted more.
# catches for if owfs is not running would be good. or bitbang.
def get_temp():
    try:
        with open('/mnt/1wire/28.49B94A040000/temperature10','r') as f:
        #with open('/mnt/1wire/28.67C6697351FF/temperature10','r') as f:
            temp = float(f.readline().strip())
            return temp + 2
    except:
        return 222

def new_temp(sensor):
    try:
        sensorpath = '/sys/bus/w1/devices/' + sensor + '/w1_slave'
        with open(sensorpath,'r') as f:
            temp_c = float(f.read().split("t=")[1].strip()) / 1000
            temp = (9.0/5.0)*temp_c + 32
            return temp
    except:
        return 999


#makes database connection, and creates the table if it doesn't exist yet.
def connectdb():
    conn = mdb.connect('chop.bad.wolf','brew','brewit','brewery');
   # cursor = conn.cursor()
   # cursor.execute('create table if not exists brewlog (id INTEGER NOT NULL AUTO_INCREMENT, brew TEXT, brewdate timestamp default CURRENT_TIMESTAMP, PRIMARY KEY (id))')
  #  cursor.execute('create table if not exists templog (brewid INTEGER, time TIMESTAMP, temp REAL, target REAL, duty INTEGER, element TEXT, FOREIGN KEY(brewid) REFERENCES brewlog(id))')
 #   cursor.execute('create table if not exists tempconfig (brewid INTEGER, target REAL, swing REAL, element TEXT, FOREIGN KEY(brewid) REFERENCES brewlog(id))')
#    cursor.execute('create table if not exists hardware (id INTEGER NOT NULL AUTO_INCREMENT, description TEXT, controlGPIO INTEGER, sensor0 TEXT, sensor1 TEXT, PRIMARY KEY (id))')
   # cursor.close()
    return conn

#updates the relevant info in the database.
def updatedb(brewid, temp, target, duty, element, sql):
    time = datetime.datetime.now()
    data =(brewid,time,temp,target,duty,element)
    cursor = sql.cursor()
    cursor.execute('INSERT INTO templog (brewid,time, temp, target, duty, element) VALUES (%s,%s,%s,%s,%s,%s)',data)
    sql.commit()
    cursor.close()


#could be moved to a database configuration. this will work for now.
def getpin(element):
    if element.lower() == "hlt":
        pin = 4
    elif element.lower() == "boil":
        pin = 1
    elif element.lower() == "test":
        pin = 7
    else:
        print "unconfigured pin"
        sys.exit()
    return pin

'''
Configures all pins as output pins and sets them to 'low'. This is to prevent any relay from being left on
unexpectedly.
'''
def turnItAllOff(jee, pin):
    print "Disabling all output pins"
    jee.config(pin, jee.OUTPUT)
    switch(jee,pin,False)

def getUserInput():
    docontinue = raw_input("Are we continuing the last brew (Yes,no)")
    if not docontinue:
        docontinue = "yes"
    if docontinue.lower() == "yes":
        #do stuff.
        print "i can't do that"
    else:
        brewinput = raw_input("What type of beer are we brewing? ")
        if not brewinput:
            brewinput = "testbrau"
        element = raw_input("Which element is this?(hlt,boil,TEST)")
        if not element:
            element = "test"

    return brewinput, element


def settarget(brewid, element, target, sql):
    data = target, brewid, element
    cursor = sql.cursor()
    cursor.execute('update tempconfig set target=%s WHERE brewid = %s AND element = %s',data)
    sql.commit()
    cursor.close()

def getsettings(brewid, element, sql):
    ids = brewid, element
    cursor = sql.cursor()
    cursor.execute('SELECT target, sensor0 FROM `tempconfig` INNER join sensors on tempconfig.sensor=sensors.id WHERE brewid = %s AND element = %s', ids)
    return cursor.fetchone()

#gets the target from the database
def gettarget(brewid, element, sql):
    ids = brewid, element
    cursor = sql.cursor()
    cursor.execute('SELECT target FROM tempconfig where brewid = %s AND element = %s',ids)
    return cursor.fetchone()[0]

'''
Sets pin to output mode, if temp is less than target+band then pin is on otherwise it's off
this runs as fast as the temp sensor will poll.
'''
def tempcontrol():
    target = 0
    database = connectdb()
    brewname, element = getUserInput()
    pin = getpin(element)
#try
    cursor = database.cursor()
    cursor.execute('INSERT INTO brewlog (brew) VALUES (%s)',[brewname] )
    brewid = cursor.lastrowid
    cursor.execute('INSERT INTO tempconfig (brewid, target, element) VALUES (%s,%s,%s)',[brewid,target,element])
    database.commit()


#etry
    settarget(brewid, element, target, database)
    print brewname + " has an id of " + str(brewid)
    print "output mode on " + element  + " pin " + str(pin)

    #there are 8 plugs on the JeeLabs Output Plug.
    gpios = 8
    #create output plug object. the address depends on the solder jumper
    jee = Adafruit_MCP230XX(address = 0x26, num_gpios = gpios, busnum = 1)
    #set all output plug pins to output and off
    turnItAllOff(jee,pin)
    #the temp swing that is allowed. ie temp +- band
    band = 0.2
    duty = 0
    target,sensor = getsettings(brewid, element, database)
    try:
        while (True):

            target,sensor = getsettings(brewid, element, database)
            #temp = get_temp()
            temp = new_temp(sensor)
            if temp != 999:
                if temp < (target - 10):
                    duty = 100
                elif (target - 10) < temp < (target - band):
                    duty = 50
                elif (target - 5) < temp < (target - band):
                    duty = 25
                elif temp > (target + band):
                    duty = 0
                else:
                    print "Operating within normal parameters."
                    duty = 0
                if target > 299:
                    duty = target - 300
                print "temp: " + str(temp) + " duty: " + str(duty) + " target: " + str(target)
                print "updating database"
                updatedb(brewid, temp, target, duty, element, database)
                switch(jee, pin, duty)
            else:
                database.commit()
                time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        turnItAllOff(jee,pin)
        database.close()
        sys.exit()

if __name__ == "__main__":
   tempcontrol()
