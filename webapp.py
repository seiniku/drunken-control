#!/usr/bin/python
from flask import *
import simplejson as json
import datetime,time
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from flask.ext.jsonpify import jsonify

app = Flask('drunken-control')
# configuration
app.config['SECRET_KEY'] = 'F34TF$($e34D';

@app.route('/latest')
def latest():
    return jsonify(getKettles())
def getconfig ():
    try:
        f= open("/home/jkeppers/drunken-control/config.yaml", 'r')
        data = load (f, Loader=Loader)
        f.close
        return data
    except IOError:
        print "Error: Cannot find config file "
        return 0
# gets info from config file and reads from the ramdisk file to get the current temp.
def getKettles():
    kettlepath='/mnt/ramdisk/'
    data = getconfig()
    for config in data:
        kettlefile=kettlepath + config
        pretemp = data[config]
        try:
            f = open(kettlefile)
            pretemp["temp"] = f.read().strip()
            f.close()
        except:
            pretemp["temp"] = "0"
    return data
@app.route('/configure', methods=['POST'])
def configure():
    newconfigs = getconfig()
    for config in newconfigs:
        newconfigs[config]["state"] = str(request.form[config + "_state"])
        newconfigs[config]["target"] = str(request.form[config + "_target"])
    try:
        f = open("/home/jkeppers/drunken-control/config.yaml", 'w')
        data = dump(newconfigs, f,  Dumper=Dumper, default_flow_style=False)
        f.close()
    except:
        print "error updating config file"
    #return redirect('/')
    return "written"

@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp


@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']


    return resp

#starts the dev web server
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)

