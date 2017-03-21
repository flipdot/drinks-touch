import datetime
import requests
import re
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

from env import is_pi

from flask import Flask
from flask import request
from flask import render_template

from users.users import Users
from database.storage import get_session
from database.storage import init_db
from database.models.recharge_event import RechargeEvent
from database.models.scan_event import ScanEvent
from database.models.drink import Drink

from stats.stats import scans

from sqlalchemy.orm import load_only, eagerload

app = Flask(__name__)

uid_pattern = re.compile("^\d+$")

@app.route('/')
@app.route('/recharge')
def index():
    users = sorted(Users.get_all(), key=lambda u: u['name'].lower())
    users.insert(0,{})
    return render_template('index.html', users=users)

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/recharge/doit', methods=['POST'])
def recharge_doit():
    user_id = request.form['user_user']
    helper_id = request.form['helper_user']
    amount = request.form['amount']
    if not user_id or not helper_id or amount <= 0:
        return 'Please enter valid data!'

    if not uid_pattern.match(user_id):
        return "Invalid user id"
    if not uid_pattern.match(helper_id):
        return "Invalid helper id"
    
    users = Users.get_all(filters=['uidNumber='+user_id])
    helpers = Users.get_all(filters=['uidNumber='+helper_id])

    if not users:
        return "user %s not found" % user_id
    if not helpers:
        return "user %s not found" % helper_id
    user = users[0]
    helper = helpers[0]
    
    session = get_session()
    ev = RechargeEvent(
        user['id'],
        helper['id'],
        amount
    )
    
    session.add(ev)
    session.commit()

    return render_template('recharge_success.html', amount=amount, user=user)

@app.route('/scans.json')
def scans_json():
    limit = int(request.args.get('limit', 1000))
    return to_json(scans(limit))

def to_json(dict_arr):
    return json.dumps(dict_arr, cls=DateTimeEncoder)

def run():
    port = 5000
    if is_pi():
        port = 80

    app.run(
        host='0.0.0.0',
        debug=not is_pi(),
        port=port
    )
