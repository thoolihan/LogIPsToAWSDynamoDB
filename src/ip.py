from flask import Flask
from flask import jsonify
from flask import request, Response
from functools import wraps
from datetime import datetime
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
app = Flask(__name__)

cred_file = open('credentials.json').read()
creds = json.loads(cred_file)

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
    return boto3.resource('dynamodb').Table('ip_log')

def log_to_aws(ip, location):
    dt = datetime.now()
    ip_log_table = get_ip_log()
    data = {"ip": ip,
            "location": location,
            "date": str(dt)}
    ip_log_table.put_item(Item = data)

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
