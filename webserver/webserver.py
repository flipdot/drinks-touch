import datetime
import random
import string

import io
import urllib

import requests
import re
import json
from datetime import datetime
import qrcode
from StringIO import StringIO

from decimal import Decimal


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

from env import is_pi

from flask import Flask, send_file, make_response
from flask import request
from flask import render_template
from flask_compress import Compress

from users.users import Users
from database.storage import get_session
from database.storage import init_db
from database.models.recharge_event import RechargeEvent
from database.models.scan_event import ScanEvent
from database.models.drink import Drink

from stats.stats import scans

from sqlalchemy.orm import load_only, eagerload

app = Flask(__name__)
Compress(app)

uid_pattern = re.compile("^\d+$")

@app.route('/')
@app.route('/recharge')
def index():
    users = sorted(Users.get_all(), key=lambda u: u['name'].lower())
    users.insert(0,{})
    print(users)
    return render_template('index.html', users=users)

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/recharge/doit', methods=['POST'])
def recharge_doit():
    user_id = request.form['user_user']
    helper_id = request.form['helper_user']
    amount = request.form['amount']
    if not user_id or not helper_id:
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

def tx_url(uid, name, info, amount=0.01):
    name = re.sub(r'[^a-zA-Z0-9 ]', '_', name)
    info = re.sub(r'[^a-zA-Z0-9 ]', '_', info)
    recipient = "flipdot e.V."
    iban = "DE07520503530001147713"
    #bic = "HELADEF1KAS"
    amount = "{:2,}".format(amount)
    reason = "drinks {uid} {name} {info}".format(uid=uid, name=name, info=info)
    return "bank://singlepaymentsepa?" + urllib.urlencode({
        'name': recipient,
        'iban': iban,
        'amount': amount,
        'reason': reason,
        'currency': 'EUR'
    })

@app.route('/tx.png')
def tx_png():
    uid = request.args.get('uid')
    name = request.args.get('name')
    amount = request.args.get('amount', "0.01")
    if not uid or not name:
        return "Please add parameters 'uid', 'name', and 'amount'!"
    uid = int(uid)
    if amount and len(amount) > 0:
        amount = Decimal(amount)
    else:
        amount = Decimal(0.01)

    info = "".join(random.choice(string.ascii_lowercase) for x in range(12))
    url = tx_url(uid, name, info, amount)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()

    img_data = io.BytesIO()
    img.save(img_data, format='PNG')
    img_data = img_data.getvalue()
    response = make_response(img_data)
    response.headers['Content-Type'] = 'image/png'
    return response

def to_json(dict_arr):
    return json.dumps(dict_arr, cls=DateTimeEncoder)

def run():
    port = 5002
    if is_pi():
        port = 80

    app.run(
        host='0.0.0.0',
        debug=not is_pi(),
        port=port
    )
