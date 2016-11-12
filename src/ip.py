from flask import Flask
from flask import jsonify
from flask import request, Response
from functools import wraps
from datetime import datetime
import os
import boto3
import json
import argparse
from boto3.dynamodb.conditions import Key, Attr
app = Flask(__name__)

cred_file = open('credentials.json').read()
creds = json.loads(cred_file)
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--local', help="set to anything to use local dynamodb")
args = parser.parse_args()
tbl_name="ip_log"

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), 'templates', filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)

def check_auth(user, password):
    return user==creds['user'] and password==creds['password']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def get_ip_log():
    if args.local:
        dyn = boto3.resource('dynamodb',
                             endpoint_url='http://localhost:8000')
    else:
        dyn = boto3.resource('dynamodb')
    return dyn.Table(tbl_name)

def log_to_aws(ip, location):
    dt = datetime.now()
    ip_log_table = get_ip_log()
    data = {"ip": ip,
            "location": location,
            "date": str(dt)}
    ip_log_table.put_item(Item = data)

@app.route('/log', methods=['GET'])
def metrics():  # pragma: no cover
    content = get_file('log.html')
    return Response(content, mimetype="text/html")

@app.route("/", methods=['GET'])
@requires_auth
def ip():
    return jsonify({'ip': request.remote_addr}), 200

@app.route("/log_ip", methods=['GET','POST'])
@requires_auth
def log_ip():
    ip = request.remote_addr
    location = request.values.get('location')
    log_to_aws(ip, location)
    return jsonify({'result': 'success',
                    'location': location,
                    'ip': ip}), 200

@app.route("/list", methods=['GET'])
@requires_auth
def home():
    location = request.values.get('location')
    ipl = get_ip_log()
    res = ipl.query(KeyConditionExpression=Key('location').eq(location),
                    ScanIndexForward=False, Limit=10)['Items']
    return jsonify(res), 200

if __name__ == "__main__":
    app.run()
