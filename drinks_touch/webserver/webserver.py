import json
import re
from datetime import datetime
from decimal import Decimal
import config

from flask import Flask, make_response
from flask import render_template
from flask import request
from flask import send_file
from flask_compress import Compress

from database.models import Tx, Account
from database.models.recharge_event import RechargeEvent
from database.storage import get_session
from env import is_pi
from stats.stats import scans
from users.qr import make_sepa_qr


app = Flask(__name__)
Compress(app)

uid_pattern = re.compile(r"^\d+$")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


@app.route("/favicon.png")
def favicon():
    return send_file("../img/favicon.png", mimetype="image/png")


@app.route("/")
@app.route("/recharge")
def index():
    accounts = Account.query.filter(Account.enabled).order_by(Account.name).all()
    return render_template("index.html", accounts=accounts)


@app.route("/stats")
def stats():
    return render_template("stats.html")


@app.route("/recharge/doit", methods=["POST"])
def recharge_doit():
    user_id = request.form.get("user_user")
    if not user_id:
        return "Bitte einen Nutzer auswählen!"
    amount = request.form.get("amount")
    if not amount:
        return "Bitte einen Betrag angeben!"

    if amount == "0":
        return "Ungültiger Betrag!"

    account = Account.query.filter(Account.id == user_id).one()

    session = get_session()
    transaktion = Tx(
        payment_reference="Aufladung via Web",
        account_id=account.id,
        amount=Decimal(amount),
    )
    session.add(transaktion)
    session.flush()
    ev = RechargeEvent(account.ldap_id, "Web UI", amount, tx_id=transaktion.id)

    session.add(ev)
    session.commit()

    return render_template("recharge_success.html", amount=amount, account=account)


@app.route("/scans.json")
def scans_json():
    limit = int(request.args.get("limit", 1000))
    return to_json(scans(limit))


@app.route("/tx.png")
def tx_png():
    uid = request.args.get("uid")
    name = request.args.get("name")
    amount = request.args.get("amount")

    if not uid or not name or not amount:
        return "Please add parameters 'uid', 'name', and 'amount'!"

    if Decimal(amount) <= 0:
        return "Please use an amount greater than 0!"

    uid = int(uid)

    img_data = make_sepa_qr(amount, name, uid)
    response = make_response(img_data.getvalue())
    response.headers["Content-Type"] = "image/png"

    return response


def to_json(dict_arr):
    return json.dumps(dict_arr, cls=DateTimeEncoder)


def run():
    port = config.WEBSERVER_PORT

    app.run(host="0.0.0.0", debug=not is_pi(), port=port)
