#!/usr/bin/python
from flask import *
import MySQLdb as mdb
import simplejson as json
import datetime,time
import threading
app = Flask(__name__)
# configuration
app.config['SECRET_KEY'] = 'F34TF$($e34D';

# Returns a connection to a mysql server. This is configured to connect to a remote server due to slow disk performance on the raspberry pi, but could be local if a faster disk is used.
def getConn():
    conn = mdb.connect('chop.bad.wolf','brew','brewit','brewery');
    return conn

#Renders the template for hlt temperatures
@app.route('/hlt')
def hlt():
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("SELECT id,brew,date_format(brewdate, '%m/%d/%Y') from brewlog ORDER BY id DESC")
    brewlist = cursor.fetchall()
    cursor.execute("SELECT id,description from sensors order by description ASC")
    sensorlist = cursor.fetchall()
    cursor.execute("select * from heating order by description ASC")
    heating = cursor.fetchall()
    conn.close()
    return render_template('hltgraph.html',brewid=brewlist,sensors=sensorlist,elements=heating)

#Does the work of updating the database to set a new temperature for the other process (simplehlt.py)
@app.route('/changehlttemp', methods=['POST'])
def changehlttemp():
    session['hlttemp'] = request.form['hlttemp']
    session['brewid'] = request.form['brewdown']
    session['sensor'] = request.form['sensordown']
    brewid = session['brewid']
    temp = session['hlttemp']
    sensor = session['sensor']
    print "update temp to " + temp + ", sensor to " + sensor
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("UPDATE tempconfig SET target=%s, sensor=%s WHERE brewid=%s",[temp,sensor,brewid])
    conn.commit()
    conn.close()
    return redirect(url_for('hlt'))

# gets the latest time and temp for a brewid from the sql connection in getconn
def getcurrentdata(brewid):
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("SELECT unix_timestamp(time)*1000,temp,target FROM templog WHERE brewid = %s ORDER BY time DESC LIMIT 1",[brewid])
    conn.close()
    return cursor.fetchone()

# gets all the data about a brewid from the database
def getalldata(brewid):
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("Select unix_timestamp(time)*1000,temp from templog where brewid=%s order by time",[brewid])
    conn.close()
    return cursor.fetchall()

# returns all data about a brewid as a json object
@app.route('/hlt_full/<int:B_id>')
def full_json(B_id):
    data = list(getalldata(B_id))
    return Response(json.dumps(data), mimetype='application/json')

# returns json for the latest time and temp of a brewid
@app.route('/hlt_new/<int:B_id>')
def latest_json(B_id):
    data = list(getcurrentdata(B_id))
    thetime = data[0]
    thetemp = data[1]
    thetarget = data[2]
    return jsonify(time=thetime, temp=thetemp, target=thetarget)
@app.route('/')
def home():
    return render_template('home.html')
#starts the dev web server
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)

